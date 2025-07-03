#!/usr/bin/env python3
"""
live_csv_exporter.py
Usage: python3 live_csv_exporter.py <ws_url> <output_csv_path>
Example: python3 live_csv_exporter.py ws://localhost:8080 test.csv

Requires: websocket-client (pip install websocket-client)

This script connections to CrossMgr during an event and exports live results to CSV files.
"""
import argparse
import json
import os
import re
import threading
from bisect import bisect_right
from websocket import WebSocketApp
import traceback

__version__ = '0.1.5'

# Global state
state = { 'catDetails': [], 'data': {}, 'curRaceTime': None }
count = 0
lock = threading.Lock()
args = None

def adapt_baseline(msg):
    """Convert baseline message into initial state, applying interpolation flags to raceTimes"""
    cats = []
    data = {}
    for name, c in msg.get('categoryDetails', {}).items():
        cats.append({
            'name': c.get('name', name),
            'pos': c.get('pos', []),
            'gapValue': c.get('gapValue', [])
        })
    for bib, r in msg.get('info', {}).items():
        rider = r.copy()
        rider['interp'] = r.get('interp', [])
        rider['raceTimes'] = r.get('raceTimes', [])
        rider['speed'] = r.get('speed', '')
        data[str(bib)] = rider
    state['curRaceTime'] = msg.get('reference', {}).get('curRaceTime')
    return {'catDetails': cats, 'data': data}

def adapt_ram(msg):
    """Convert ram update into partial state"""
    cats = []
    data = {}
    for key, c in msg.get('categoryRAM', {}).get('m', {}).items():
        cats.append({
            'name': c.get('name', key),
            'pos': c.get('pos', []),
            'gapValue': c.get('gapValue', [])
        })
    # a for add, m for modify
    for k in ['a', 'm',]:
        for bib, r in msg.get('infoRAM', {}).get(k, {}).items():
            rider = r.copy()
            rider['raceTimes'] = r.get('raceTimes', [])
            rider['interp'] = r.get('interp', [])
            rider['speed'] = r.get('speed', '')
            data[str(bib)] = rider
    state['curRaceTime'] = msg.get('reference', {}).get('curRaceTime', state['curRaceTime'])
    return {'catDetails': cats, 'data': data}

def merge_partial(partial):
    """Merge incremental partial into global state"""
    for new_cat in partial.get('catDetails', []):
        names = [c['name'] for c in state['catDetails']]
        if new_cat['name'] in names:
            idx = names.index(new_cat['name'])
            state['catDetails'][idx] = new_cat
        else:
            state['catDetails'].append(new_cat)
    for bib, rider in partial.get('data', {}).items():
        state['data'][bib] = rider

def build_csv():
    """Serialize full state into CSV, including only completed lap times"""
    categories = {}
    crt = state.get('curRaceTime')
    for cat in state['catDetails']:
        max_laps = 0
        cat_name = cat.get('name', '')
        if cat_name not in categories:
            categories[cat_name] = []
        for bib in cat.get('pos', []):
            r = state['data'].get(str(bib))
            if r and 'raceTimes' in r:
                max_laps = max(max_laps, len(r['raceTimes']) - 1)
        #rows = categories[cat_name]
        rows = categories[cat_name]
        max_laps = 0
        for idx, bib in enumerate(cat.get('pos', []), start=1):
            d = state['data'].get(str(bib), {})
            rt = d.get('raceTimes', [])
            interp = d.get('interp', [])
            if crt is not None and crt > 0 and rt:
                completed = bisect_right(rt, crt)
            else:
                completed = len(rt)

            lap_times = [ rt[0] if i == 0 else rt[i] - rt[i-1] for i in range(0, completed) ]

            if len(interp) > 0:
                interpLast = interp[completed-1] if len(interp) > completed-1 else False
            else:
                interpLast = False

            status = d.get('status', '')
            vals = []
            def vals_append(val, fmt=None):
                if args.padding and fmt is not None:
                    val = f'{str(val):{fmt}}'
                vals.append(f'"{val}"' if type(val) is str else f'{val}') 
                pass
            # Cat name
            safe = cat_name.replace('"','""')
            vals_append(f'{safe}')
            #idx_str = f'"({str(idx)})"' if interpLast else f'"{str(idx)}"'
            idx_str = f'({str(idx)})' if interpLast else idx

            vals_append(idx_str, "^6s")
            vals_append(bib, "^6s")

            fullname = f"{d.get('LastName','')},{d.get('FirstName','')}".strip()
            safe = fullname.replace('"','""')
            vals_append(safe, "<20s")

            team = f"{d.get('Team','')}".strip()
            safe = team.replace('"','""')
            vals_append(safe,"<30s")

            def fmt(num):
                """Format a number to one decimal, blank if invalid"""
                try:
                    m = num/60 if num > 60 else 0
                    s = num % 60
                    return f"{m:.0f}:{s:02.0f}"
                except Exception as e:
                    print(f"Error formatting number: {num} e: {e}")
                    return ''
            # total time
            total = f'{fmt(rt[-1] if rt else 0)}'
            vals_append(total)

            # gap
            gv = cat.get('gapValue', [])
            gap = gv[idx-1]
            processed_gap = re.sub(r'(\d+\.\d)\d+', r'\1', str(gap))
            vals_append(processed_gap, ">4s")

            # speed
            raw_speed = d.get('speed','')
            raw_speed = f'"{raw_speed}"'
            processed_speed = re.sub(r'(\d+)\.\d+', r'\1', raw_speed)
            vals.append(f'{processed_speed:>8s}')

            if not args.no_laptimes:
                # Lap times
                for i in range(1, max_laps + 1):
                    if i < completed:
                        lap_time = lap_times[i]
                        val = f'({fmt(lap_time)})' if interp[i] else f'{fmt(lap_time)}'
                    else:
                        val = ''
                    vals_append(val, "^9s")
            if status != 'Finisher':
                vals_append(status)
            if completed > max_laps:
                max_laps = completed
            rows.append(args.csv_delimiter.join(vals))

        # Header row
        headers = ['Category','Pos','Bib','Name','Team','Time','Gap','Speed']
        step = 1
        if not args.no_laptimes:
            headers += [f"Lap{i}" for i in range(1, max_laps, step)]
        header_row = args.csv_delimiter.join(headers)
        categories[cat_name] = [header_row] + rows

    results = {}
    for cat_name, rows in categories.items():
        results[cat_name] = '\r\n'.join(rows)
    return results


def on_message(ws, raw):
    """ process incoming WebSocket messages """
    global count
    try:
        msg = json.loads(raw)
    except json.JSONDecodeError:
        return
    try:
        partial = None
        # Baseline message
        if msg.get('cmd') == 'baseline':
            partial = adapt_baseline(msg)
            with lock:
                state['catDetails'] = partial['catDetails']
                state['data'] = partial['data']
                count = 0
        # Incremental ram update
        elif msg.get('cmd') == 'ram':
            partial = adapt_ram(msg)
            with lock:
                merge_partial(partial)
        else:
            return
    except Exception as e:
        print(f"Error processing message: {e}")
        print(traceback.format_exc())
        return

    # Write snapshot
    base, ext = os.path.splitext(args.output)
    with lock:
        if args.save_json:
            with open(f"{base}.json", 'w' if count == 0 else 'a', encoding='utf-8') as f:
                json.dump(msg, f, ensure_ascii=False, indent=4)
        try:
            results = build_csv()
            count += 1
            def gen_out_name(base, cat_name, count, ext):
                """Generate output filename based on base name, category, and count"""
                number = f"-{count:05d}" if args.save_numbered else ''
                return f"{base}-{cat_name}{number}{ext}.csv".replace(' ', '_').replace('/', '-').replace('(', '').replace(')', '')

            for cat_name, csv in results.items():
                if args.only_all and 'All' not in cat_name:
                    continue
                if args.only_others and 'All' in cat_name:
                    continue
                out_name = gen_out_name(base, cat_name, count, ext)
                with open(out_name, 'w', encoding='utf-8') as f:
                    f.write(csv + '\n')
                if args.verbose:
                    print(f"Wrote CSV #{count}: {out_name}")

                # remove old versions if save_numbered is set
                if args.save_numbered and args.save_numbered > 0 and count > args.save_numbered:
                    for i in range(count-args.save_numbered, 0, -1):
                        out_name = gen_out_name(base, cat_name, i, ext)
                        if args.verbose:
                            print(f"Checking for CSV #{i} to remove... {out_name}")
                        if not os.path.exists(out_name):
                            break
                        try:
                            os.remove(out_name)
                            if args.verbose:
                                print(f"Removed CSV #{i}: {out_name}")
                        except PermissionError as e:
                            print(f"Permission error removing CSV #{i}: {e}")
                        except Exception as e:
                            print(f"Error removing CSV #{i}: {e}")

        except Exception as e:
            print(f"Error writing CSV: {e}")
            print(traceback.format_exc())


def on_open(ws):
    # Request baseline when connection first opened
    ws.send(json.dumps({'cmd': 'send_baseline', 'raceName': 'CurrentResults'}))

def main():
    parser = argparse.ArgumentParser(
            prog='live_csv_exporter',
            description='Live CSV exporter for CrossMgr events',
            epilog=(
            f"Version: {__version__}\n\n"
            "Example: python3 live_csv_exporter.py ws://localhost[:8766] results.csv\n"
            "The socket will default to 8766 if not specified.\n"
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('url', help='WebSocket URL wss://example.com:8766 or ws://localhost[:8766]')
    parser.add_argument('output', help='Base output CSV path')
    parser.add_argument('--save_json', action='store_true', help='Save messages in json file.')
    parser.add_argument('--save_numbered', nargs='?', const=4, type=int, help='Save numbered CSV files, keeping the last N files. Default is 4. -1 to keep all files')    

    parser.add_argument("--only_all", action='store_true', help="only include rows where Criteria == 'All'")
    parser.add_argument("--only_others", action='store_true', help="exclude rows where Criteria == 'All'")
    parser.add_argument("--csv_delimiter", action='store', default=',', help="CSV delimiter to use, default is ','")
    parser.add_argument("--padding", action='store_true', help="Pad CSV columns to fixed width, default is no padding")
    parser.add_argument("--no_laptimes", action='store_true', help="Do not include lap times in CSV output, only total time and gaps")

    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--verbose', action='store_true', help='Verbose messages.')
    parser.add_argument('--quiet', action='store_true', help='No messages.')
    global args
    args = parser.parse_args()

    url = re.sub(
        r'^(wss?://[^/:]+)' r'(?=(?:$|/))',     # lack of comma intentional 
        rf'\1:{8766}',
        args.url
    )
    if not args.quiet:
        if args.save_json:
            print(f"Saving JSON messages in JSON format to file name prefix {args.output}.")
        if args.save_numbered and args.save_numbered > 0:
            print(f"Saving to numbered files, will retain the last {args.save_numbered} files.")
        elif args.save_numbered == -1:
            print("Saving to numbered files, retaining all files.")
        print(f"Connecting to WebSocket URL: {url}")

    ws_app = WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=lambda ws, e: print('Error:', e),
        on_close=lambda ws, code, msg: print('Closed:', code)
    )
    ws_app.run_forever()

if __name__ == '__main__':
    main()

