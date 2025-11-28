import web browser 
import tempfile 
import os 
 
 
with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f: 
    f.write(HTML_CONTENT) 
    webbrowser.open('file://' + f.name) 
