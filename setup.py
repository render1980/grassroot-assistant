from distutils.core import setup

setup(name='grassroot-assistant',
      version='1.0',
      py_modules=['main', 'redis_client'],
      data_files=[('config', ['requirements.txt'])],
      url='https://t.me/GrassrootsAssistantBot',
      author='render1980',
      license='MIT',
      author_email='render1980@gmail.com'
      )
