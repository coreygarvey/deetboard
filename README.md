# DeetBoard

Welcome to DeetBoard, a web application built to connect teams with internal product experts.

## Objective
DeetBoard connects any team with those who are most knowledgable about the software. No longer are colleagues faced with uncertainty when searching for answers. Deetboard's single location of product knowlege allows team members to keep track of updates and reacquaint themselves with mature product features.

Head to [deetboard.com](https://deetboard.com) and create a new team. Build a product, add features, and upload screenshots to improve the discussion.

## Project Details
Application logic exists primarily int he */Âdeetboard/* directory. Apps are built according to objects within the project. 

URL routes can be viewed within the */deetboard/deetboard/urls.py* file.

## Technologies
* Backend
	* [Python Django](https://www.djangoproject.com/)
	* [PostgreSQL](https://www.postgresql.org/)
	* [Virtualenv](https://virtualenv.pypa.io/en/stable/), [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)
	* [Celery](http://docs.celeryproject.org/en/latest/)
	* [Redis](https://redis.io/)
	* [Stripe](https://stripe.com/)
* Front end
	* [Annotorious](https://annotorious.github.io/)
* Hosting
	* [Amazon Linux AMI](https://aws.amazon.com/amazon-linux-ami/)
	* [Amazon RDS - PostgreSQL](https://aws.amazon.com/rds/postgresql/)
	* [NGINX](https://www.nginx.com/)
	* [Gunicorn](http://gunicorn.org/)

## Future of DeetBoard
This remains in development and all feedback is welcome. A few plans for future development include:
* Activation of monthly Stripe subscriptions
* Complete Annotorious to support conversations between experts and other users
* Mobile application support

## Contact
For all questions, comments, and feedback please email corey@coreygarvey.com