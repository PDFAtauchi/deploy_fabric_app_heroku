import os
import random
import string

from fabric.api import env, local, require, lcd, run
from fabric.colors import cyan, green
from fabric.operations import prompt
from fabric.contrib.files import append, exists


current_dir = os.getcwd()
print('----'*10)
print(current_dir)
env.project_name = 'superlists-prod'
env.environment = 'prod'
env.branch = 'master'
env.repo_project = 'https://github.com/PDFAtauchi/Practice_Testing'


def serve():
	local('python manage.py runserver')


def unit_test():
	"""
	Runs unit tests
	"""
	print(cyan('start unit tests...'))
	local('python manage.py test lists')
	print(green('passed unit tests'))

def functional_test():
	"""
	Runs functional tests
	"""
	print(cyan('start functional tests...'))
	local('python manage.py test functional_tests/')
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
	'''
	if exists('.git'):
		local('git fetch')
		print(green('Finish pull repository'))
	else:
		local('git clone {env.repo_project} .')
		print(green('cloned repository'))  
	current_commit = local("git log -n 1 --format=%H", capture=True)  
	local('git reset --hard {current_commit}')
	print(green('FInish lastest source'))
	'''
	pull()


def write_requirements_environment(requirement_file, environment):
    with open(requirement_file, 'w') as f:
        f.write('-r requirements/'+environment+'.txt')

def write_dot_env_file(env_file, environment):
    settings = set_settings(environment)
    with open(env_file, 'w') as f:
        for k, v in settings.items():
            f.write('{0}={1}\n'.format(k.upper(), v))

def update_virtualenv():
	#environment
	
	#if not exists('venv_production/Scripts/pip'):
	#	local('virtualenv venv_production')

	#requirements
	requirement_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
	write_requirements_environment(requirement_file, env.environment)
	#local('venv_production/Scripts/pip install -r requirements.txt')
	
	print(green('Finish update virtualenv + requirements'))

def generate_secret_key():
    specials = '!@#$%^&*(-_=+)'
    chars = string.ascii_lowercase + string.digits + specials
    return ''.join(random.choice(chars) for _ in range(50))


def switch_debug(argument):
    switcher = {
        'prod': False,
        'stg': False,
        'dev': True,
    }
    return switcher.get(argument, True)

def switch_allowed_host(argument):

	domain = env.project_name+".herokuapp.com"
	switcher = {
        'prod': domain,
        'stg': domain,
        'dev': "*, localhost, 127.0.0.1",
    }
	return switcher.get(argument, '*, localhost, 127.0.0.1')


def set_settings(environment):
    DEBUG = switch_debug(environment)
    ALLOWED_HOSTS = switch_allowed_host(environment)

    return {
        'SECRET_KEY': generate_secret_key(),
        'DEBUG': DEBUG,
        'ALLOWED_HOSTS': ALLOWED_HOSTS,
        'ENVIRONMENT':env.environment,
    }

def create_or_update_dotenv():
	env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
	write_dot_env_file(env_file, env.environment)
	print(green('Finish create .env'))

def create_standard_server():
	"""
	Creates a sever with a standard build
	"""
	
	get_latest_source()
	update_virtualenv()
	create_or_update_dotenv()

	#unit_test()
	#functional_test()

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

	print(cyan('Creating new server'.format(env.project_name)))
	try:
		#heroku repo:reset -a APPNAME
		local('heroku apps:delete --app {0}'.format(env.project_name))
		#heroku apps:destroy app1
	except:
		pass
	
	print(cyan('Creating new server'.format(env.project_name)))
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
	local('heroku config:set DJANGO_SECRET_KEY="{}" --remote '.format(create_secret_key()))
	
	
def pull():
	#print(cyan('Start Pull from Repo {0}'.format(env.repo_project)))
	#local('git pull origin {0}'.format(env.branch))
	print(green('Finish pull'))


def push():
	print(cyan('Pushing to Heroku...'))
	#local('git push heroku master {0}'.format(env.project_name))
	#local('git push heroku {0}:master'.format(env.branch))
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