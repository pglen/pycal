#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

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
	find . -type d -name "__pycache__" -exec ls  {} \;
	@rm -rf build/*

install:
	@python3 ./install.py

local-install:
	pip install .

local-uninstall:
	pip uninstall pyvcal

pack:
	@./pack.sh

git:
	git add .
	git commit -m autocheck
	git push
	#git push local

# End of Makefile







