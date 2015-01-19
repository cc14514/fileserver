EPYDOC=epydoc  
DSTDOC=../statics/lcmcs

doc: clean-doc  
	$(EPYDOC) --html --graph=all -v -o $(DSTDOC) views.py  

clean-doc:  
	rm -rf $(DSTDOC)  

clean: clean-doc  
	find . \( -name '*~' -or \  
	-name '*.pyc' -or \  
	-name '*.pyo' \) \  
	-print -exec rm {} \; 
