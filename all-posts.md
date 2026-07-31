---
layout: default
title: All Posts
---

{% for post in site.posts %}
<a href="{{ post.url }}">{{ post.title }}</a><br>
{% endfor %}