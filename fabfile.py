import os
import random
import string

from fabric.api import env, local, require, lcd, run
from fabric.colors import cyan, green
from fabric.operations import prompt
from fabric.contrib.files import append, exists

current_dir = os.getcwd()
env.project_name = 'deploy-polls-simple'
env.environment = 'prod'
env.branch = 'master'
env.repo_project = 'https://github.com/PDFAtauchi/deploy_fabric_app_heroku.git'


def serve():
	local('python manage.py runserver')


def unit_test():
	"""
	Runs unit tests
	"""
	print(cyan('start unit tests...'))
	pass
	print(green('passed unit tests'))

def functional_test():
	"""
	Runs functional tests
	"""
	print(cyan('start functional tests...'))
	pass
	print(green('passed functional tests'))


def deploy():
	"""
	Deploys servers
	"""
	print(cyan('Initializing Deploy...', bold=True))
	create_standard_server()
	
	print(green('Deploy complete'))

def get_latest_source():
	"""
	Update or clone repository
	"""
	print(cyan('Update latest source'))
	pull()

def create_standard_server():
	"""
	Creates a sever with a standard build
	"""
	
	get_latest_source()

	create_server()
	push()
	migrate()
	collectstatic()
	create_superuser()
	#ps()
	#open_heroku()


def create_server():
	"""
	Creates a new server on heroku
	"""

	print(cyan('Creating new server {0}'.format(env.project_name)))
	try:
		#heroku repo:reset -a APPNAME
		local('heroku apps:delete --app {0}'.format(env.project_name))
		#heroku apps:destroy app1
	except:
		pass
	
	print(cyan('Creating new server {0}'.format(env.project_name)))
	local('heroku create {0}'.format(env.project_name))
	local('git remote -v')
	print(green('created server'))


def configure_sever():
	"""
	Configures server with a general configuration
	"""
	local('heroku addons:create heroku-postgresql --remote {0}'.format(env.branch))
	local('heroku pg:backups schedule DATABASE --at "04:00 UTC" --remote {0}'.format(env.branch))
	local('heroku pg:promote DATABASE_URL --remote {0}'.format(env.branch))
	local('heroku addons:create redistogo:nano --remote {0}'.format(env.branch))
	local('heroku addons:create newrelic:wayne --remote ')
	local('heroku config:set NEW_RELIC_APP_NAME="{}" --remote {0}'.format(env.project_name, env.branch))
	local('heroku config:set DJANGO_CONFIGURATION=Production --remote {0}'.format(env.branch))
	#local('heroku config:set DJANGO_SECRET_KEY="{}" --remote '.format(create_secret_key()))
	
	
def pull():
	print(cyan('Start Pull from Repo {0}'.format(env.repo_project)))
	local('git pull origin {0}'.format(env.branch))
	print(green('Finish pull'))


def push():
	print(cyan('Pushing to Heroku...'))
	local('heroku git:remote -a {0}'.format(env.project_name)) #Connect this local repository to your remote heroku respotory
	local('heroku config:set DISABLE_COLLECTSTATIC=1 --app {0}'.format(env.project_name))
	local('git push  heroku master')
	print(green('Finish push to heroku master'))
  
def migrate():
	local('heroku addons:create heroku-postgresql:hobby-dev --app {0}'.format(env.project_name))
	local('heroku run python manage.py migrate  --noinput --app {0}'.format(env.project_name))
	print(green('Finish migrate'))

def collectstatic():
	local('heroku run python manage.py collectstatic --noinput --app {0}'.format(env.project_name))
	print(green('Finish collectstatic'))

def create_superuser():
	local('heroku run python manage.py '
		  'createsuperuser --app {0}'.format(env.project_name))
	print(green('Finish create superuser'))

def ps():
	"""
	Scales a web dyno on Heroku
	"""
	#local('heroku ps:scale web=1 --app {0}'.format(env.project_name))
	#local('heroku ps --app )
	print(green('Finish heroku scale'))

def open_heroku():
	local('heroku open --app {0}'.format(env.project_name))
	print(green('Finish open'))

	#heroku restart --app superlists-prod
	#python manage.py check --deploy