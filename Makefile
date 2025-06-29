# vim: shiftwidth=8 tabstop=8 noexpandtab textwidth=0

#

#VERSION=$(shell  ./Version.py version)
#APP_VER=$(shell  ./Version.py AppVerName)
#AppVerName="CrossMgr 3.1.64-private"

APPNAME = liveresultscapture

VER=$(shell  sed -nE "s/^__version__\s*=\s*['\"]([^'\"]+)['\"].*/\1/p" app/$(APPNAME).py)
EXES = $(APPNAME).exe 
ZIPFILE = ${APPNAME}-${VER}.zip

all: ${EXES} 

%.exe : app/%.py
	time -p python -m nuitka \
		--onefile \
		--windows-icon-from-ico=./images/light.png \
		$<
	belcarra-signtool $@
	zip ${ZIPFILE} $@

test:
	@echo APPNAME: ${APPNAME}
	@echo VER: ${VER}
	@echo EXES: ${EXES}
	@echo ZIPFILE: ${ZIPFILE}

#$(ZIPNAME): ${EXES}
#	zip $@ $^

clean:
	-rm -rf *build *dist *.exe *.zip

really-clean: clean
	-rm -rf *.exe


