import configparser
env = configparser.ConfigParser()
env.read('.env')


print(env['ELISYUM']['PUBLIC_KEY'])