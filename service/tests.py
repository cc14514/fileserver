"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

# from django.test import TestCase
# 
# 
# class SimpleTest(TestCase):
#     def test_basic_addition(self):
#         """
#         Tests that 1 + 1 always equals 2.
#         """
#         self.assertEqual(1 + 1, 2)
import imghdr
import urllib
if __name__ == '__main__':
    try: 
        url='http://c.hiphotos.baidu.com/baike/w%3D261/sign=4b4bd045d01373f0f53f6899950f4b8b/86d6277f9e2f0708b230623ee824b899a901f2d3.jpg'
        urlopen=urllib.URLopener() 
        fp = urlopen.open(url) 
        data = fp.read() 
        fp.close() 
        file=open('/app/ahaha','w+b') 
        file.write(data) 
        file.close() 
        print imghdr.what('/app/1.docx') 
    except IOError, error: 
        print "DOWNLOAD %s ERROR!==>>%s" % (url, error) 
    except Exception, e: 
        print "Exception==>>" + e 
        
        
def downloadFileByUrl(url):
    try: 
        urlopen=urllib.URLopener() 
        fp = urlopen.open(url) 
        data = fp.read() 
        fp.close() 
        return data
    except IOError, error: 
        logger.error("DOWNLOAD %s ERROR!==>>%s" % (url, error)) 
    except Exception, e: 
        logger.error("Exception==>>" + e) 
    