# HAICO

The Hugo and Infoscreen content organizer (HAICO) is a
[Django](https://www.djangoproject.com/) project for managing several
information channels of an organisation:

- A **static website** which is built with the
  [Hugo static site generator](https://gohugo.io/) that provides general
  information and news from groups within that organisation (some form of a
  blog within an organisation).
- [**Infoscreens**](https://en.wikipedia.org/wiki/Digital_signage) which are
  located inside the organisation that display some kind of multimedia content.

The basic idea is to teaser some information on the infoscreens and let the
user read more information about it on the website. One goal of this project is
to provide some kind of connection between these information sources.

## Features

### Currently implemented

- A guided form for submitting infoscreen content with basic file verification
- A list view for current/all infoscreen content with json export functionality
- German translation
- OpenID/OAuth2 authentication
- Creating infoscreens where only admins can upload content
- Setting default display time for infoscreen content for each screen
- fair scheduling of using defualt display time and videolength differentiating between regular content and event advertisement
- Automatically generating config files for [static-infoscreen](https://github.com/hd1ex/static-infoscreen) for each infoscreen via cron or triggered by upload
- to start cron job execute `python manage.py crontab add` and to stop `python manage.py crontab remove`

### Planned

- An **image board** view for current infoscreen content: The idea is that
  users can scan a qr code pointing to that website and get a view with
  previews of all infoscreen content. If the user clicks on one, it is
  forwarded to the related post on the website.
- A form for creating and updating a **post on the website**: This is basically
  a markdown and (probably) metadata editor which stores the content in files
  for Hugo.
  [Martor](https://github.com/agusmakmun/django-markdown-editor) looks
  promising for doing this kind of job.
- Automatic **scheduling** of infoscreen content: The idea is to feed the
  [API of PiSignage](https://piathome.com/apidocs/) with the content from the
  database.
  
## Contributing

Please read [Contributing.md](Contributing.md) for this.
