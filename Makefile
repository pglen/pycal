#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

.PHONY: docs

all:
	@echo "Type 'make help' for a list of targets"

help:
	@echo
	@echo "Targets:"
	@echo "	 make install    --    Install  "
	@echo "	 make pack       --    package  "
	@echo "	 make clean      --    rm py temps  "
	@echo "	 make git        --    check in to repo  "
	@echo

clean:
	@find . -type d -name "__pycache__" -exec rm -f {}/* \;
	@rm -rf build/*
	@rm -rf pyvcal.egg-info/
	@rm -f README.preview.html

install:
	@python3 ./install.py

local-install:
	pip install .

local-uninstall:
	pip uninstall pyvcal

pack:
	@./pack.sh

# Auto Checkin
ifeq ("$(AUTOCHECK)","")
    AUTOCHECK=autocheck
endif

test:
	@echo "AUTOCHECK =" $(AUTOCHECK)
	@echo "MODPATH = " $(MODPATH)

git:
	git add .
	git commit -m $(AUTOCHECK)
	git push
	#git push local

# Get path to pyvguicom
MODPATH=$(shell python getmodpath.py pyvguicom)
QQQ=$(shell which pdoc)
PPP=PYTHONPATH=pyvcal:./:$(MODPATH) python3 -W ignore::DeprecationWarning $(QQQ) --force --html

docs:
	@${PPP} -o pyvcal/docs/ pyvcalgui.py
	@${PPP} -o pyvcal/docs/ pyvcal/calfile.py
	@${PPP} -o pyvcal/docs/ pyvcal/comline.py
	@${PPP} -o pyvcal/docs/ pyvcal/pycalent.py
	@${PPP} -o pyvcal/docs/ pyvcal/pycalsql.py
	@${PPP} -o pyvcal/docs/ pyvcal/calfsel.py
	@${PPP} -o pyvcal/docs/ pyvcal/pycallog.py
	@${PPP} -o pyvcal/docs/ pyvcal/calutils.py
	@${PPP} -o pyvcal/docs/ pyvcal/pyala.py
	@${PPP} -o pyvcal/docs/ pyvcal/pycal.py

# End of Makefile
