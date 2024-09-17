from posts import *

with open("template.html",mode="r") as file:
    template = file.read()

body = """<p>
This is the body of my HTML webpage.
</p>
<img src="https://ssl.gstatic.com/ui/v1/icons/mail/rfr/logo_gmail_lockup_dark_2x_r5.png">"""

heading = "This is my article!"

article = template
article = article.replace("{$HEADING$}",heading)
article = article.replace("{$BODY$}",body)
with open("post.html",mode="w") as file:
    file.write(article)

print("Done.")