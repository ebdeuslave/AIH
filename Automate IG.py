import argparse
import importlib
import os
import sys
import subprocess
from getpass import getpass
from time import sleep, time
import winsound as ws
from playsound import playsound as ps
from gtts import gTTS
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver


print(
    '''
USAGE : python autoig.py YOUR_IG_USERNAME
        Password : TYPE YOUR PASSWORD (it will not appear for security purpose)
        Type seconds between messages
''')

if not importlib.util.find_spec('selenium'):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'selenium'])
if not importlib.util.find_spec('gtts'):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'gTTS'])
if not importlib.util.find_spec('playsound'):
    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', 'playsound'])


parser = argparse.ArgumentParser()
parser.add_argument("username", help="Your IG Username")
args = parser.parse_args()
username = args.username
password = getpass()


def followersIG(userN, passwd, timeinSeconds):
    if not os.path.isfile(f'{userN}_followers.txt'):
        sys.exit(f'<{userN}>\'s Followers File not found\nPlease put followers file to the same directory and name it : {userN}_followers.txt')
    else:
        ################ Login ################
        print('Hello', userN)
        chrome_options = Options()
        # hide infos and DevTools msg
        chrome_options.add_argument('--log-level=3')
        # chrome_options.add_argument('--headless')
        chrome_options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(
            executable_path='C:/chromedriver.exe', options=chrome_options)
        driver.get('https://instagram.com/')
        WebDriverWait(driver, 1000).until(
            EC.presence_of_element_located((By.NAME, 'username')))
        print('Login-in..')
        username = driver.find_element_by_name('username').send_keys(userN)
        sleep(1)
        password = driver.find_element_by_name('password').send_keys(passwd)
        sleep(1)
        submit = driver.find_element_by_xpath(
            '//*[@id="loginForm"]/div/div[3]/button').click()
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, 'slfErrorAlert')))
            print('Incorrect username or password, please try running script again..')
            driver.quit()
            sleep(.5)
            os._exit(0)
        except:
            WebDriverWait(driver, 60).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="react-root"]/section/nav/div[2]/div/div/div[1]/a/div/div/img')))
        print('Logged-In Successful')
        print('Importing Usernames from text file..')
        with open(f'{userN}_followers.txt', 'r') as f:
            usersList = f.readlines()
            for i in range(len(usersList)):
                usersList[i] = usersList[i].replace('\n', '')

        print('#####################################################\n\n')
        print(f'List of Users : \n\n{usersList}\n')
        print(
            f'Number of Followers imported from text file : {len(usersList)} Followers\n')
        print('#####################################################\n\n')
        driver.get('https://instagram.com/direct/new/')
        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.NAME, 'queryBox')))
        sleep(2)
        try:
            driver.find_element_by_xpath(
                '/html/body/div[6]/div/div/div/div[3]/button[2]').click()
        except:
            pass
        print('Starting sending messages..')
        print('#####################################################\n\n')
        for user in usersList:
            # Send msg btn
            print(f'Sending message to <{user}>..')
            driver.get('https://instagram.com/direct/new/')
            WebDriverWait(driver, 100).until(
                EC.presence_of_element_located((By.NAME, 'queryBox')))
            driver.find_element_by_name('queryBox').send_keys(user)
            WebDriverWait(driver, 100).until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[2]/div/div/div[2]/div[2]/div/div/div[3]/button')))
            sleep(1)
            driver.find_element_by_xpath(
                '/html/body/div[2]/div/div/div[2]/div[2]/div/div/div[3]/button').click()
            sleep(1)
            # Next
            driver.find_element_by_xpath(
                '/html/body/div[2]/div/div/div[1]/div/div[2]/div/button').click()
            WebDriverWait(driver, 1000).until(
                EC.presence_of_element_located((By.TAG_NAME, 'textarea')))
            msgElement = driver.find_element_by_tag_name('textarea')
            msg = 'TEST MSG'
            #newLine = ActionChains(driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).perform()
            sleep(1)
            msgElement.send_keys(msg)
            with open(f'lastUser_{userN}.txt', 'w') as l:
                l.write(user)
            print('Message Sent!')
            sleep(timeinSeconds)

        print('#############################################')
        print('Bot finished the job ! GoodBye', userN)
        print('#############################################')
        for _ in range(2):
            ws.Beep(1000, 500)
        gTTS(text=f'The Program has finished its job ! GoodBye {userN}').save(
            'done.mp3')
        ps('done.mp3')


try:
    timeS = int(input('Give me time in seconds to wait between messages (NOTE : it is secure to put +15 seconds to prevent blocking your account by Instagram system) : '))
except:
    timeS = 15

followersIG(username, password, timeS)
