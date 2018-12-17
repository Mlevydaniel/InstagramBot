import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep, strftime
from random import randint
import pandas as pd
import json
from datetime import datetime

# Load hashtag list
try:
    f = open("/Users/martin/Documents/Instagram Bot/hashtag_list.txt", "r")
    contents = f.read().split(',')
    hashtag_list = [i.strip() for i in contents]
except:
    print('Please, create a txt file called hashtag_list in your directory with the hashtag to navigate on')

# Load the username and password from a JSON file. Otherwise, ask for it
try:
    json_data = open('/Users/martin/Documents/Instagram Bot/user.json').read()
    data = json.loads(json_data)
    user = input('Enter a user: ')
except:
    print('Please, create a txt file called hashtag_list in your directory with the hashtag to navigate on')

# Load previous data or create a new list
try:
    user_list = pd.read_csv('/Users/martin/Documents/Instagram Bot/user_list.csv', header=None)   # load whole database of users connected
    users_followed = [user_list[1][i] for i in range(0, len(user_list))] # get the list of usernames already followed
except:
    print('No preexisten user list detected. The code will create a new one after finishing')
    users_followed = []

# Start navigation
chromedriver_path = '/anaconda3/bin/chromedriver' # Change this to your own chromedriver path!
webdriver = webdriver.Chrome(executable_path = chromedriver_path)
sleep(2)

# Get in the webpage
webdriver.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
sleep(3)

# Login
username = webdriver.find_element_by_name('username')
username.send_keys(data[user]['username'])
password = webdriver.find_element_by_name('password')
password.send_keys(data[user]['password'])

button_login = webdriver.find_element_by_css_selector('#react-root > section > main > div > article > div > div:nth-child(1) > div > form > div:nth-child(3) > button')
button_login.click()
sleep(3)

notnow = webdriver.find_element_by_css_selector('body > div:nth-child(13) > div > div > div > div.mt3GC > button.aOOlW.HoLwm')
notnow.click() #comment these last 2 lines out if you don't get a pop up asking about notifications

new_followed = []  # list with new users information and connected time

tag = -1
followed = 0
likes = 0
comments = 0

for hashtag in hashtag_list:
    tag += 1
    webdriver.get('https://www.instagram.com/explore/tags/'+ hashtag_list[tag] + '/')  # get in the hashtag webpage
    print('Starting new hashtag: {}'.format(hashtag))
    sleep(5)
    first_thumbnail = webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div') # select the first image

    first_thumbnail.click()
    sleep(randint(1,2))
    try:
        # navigate in the hashtag page 200 times
        for x in range(1, 5):
            username = webdriver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/article/header/div[2]/div[1]/div[1]/h2/a').text # get the username of the post

            # check if the user is in list. In that case, next picture
            if username not in users_followed:

                # If we already follow, do not unfollow and next picture
                if webdriver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/article/header/div[2]/div[1]/div[2]/button').text == 'Follow':

                    webdriver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/article/header/div[2]/div[1]/div[2]/button').click() # follow the user

                    followed += 1

                    # Liking the picture
                    button_like = webdriver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/article/div[2]/section[1]/span[1]/button/span')
                    button_like.click()

                    likes += 1
                    sleep(randint(18,25))

                    # Comments and tracker
                    comm_prob = randint(1,10)  # Choose the comment by random
                    print('{}_{}: {}'.format(hashtag, x, comm_prob))  # print the hashtag, num of iteration and comment probability
                    if comm_prob > 7:
                        comments += 1
                        webdriver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/article/div[2]/section[1]/span[2]/button/span').click()       # do a click in the comment button
                        comment_box = webdriver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/article/div[2]/section[3]/div/form/textarea')    # find the comment area

                        # Select the comment based on the probability
                        if (comm_prob < 7):
                            message = 'Really cool!'
                            comment_box.send_keys(message)
                            sleep(1)
                        elif (comm_prob >= 7) and (comm_prob < 9):
                            message = 'Nice work :)'
                            comment_box.send_keys(message)
                            sleep(1)
                        elif comm_prob == 9:
                            message = 'Nice gallery!!'
                            comment_box.send_keys(message)
                            sleep(1)
                        elif comm_prob == 10:
                            message = 'So cool! :)'
                            comment_box.send_keys(message)
                            sleep(1)

                        # Enter to post comment
                        comment_box.send_keys(Keys.ENTER)
                        sleep(randint(22,28))

                    tupla = (username, str(datetime.now()), message, comm_prob)
                    new_followed.append(tupla)

                # Next picture
                webdriver.find_element_by_link_text('Next').click()
                sleep(randint(25,29))

            else:
                webdriver.find_element_by_link_text('Next').click()
                sleep(randint(20,26))

    # some hashtag stops refreshing photos (it may happen sometimes), it continues to the next
    except:
        continue  # starts all again with the next hashtag

# Append new users to the list (Should not be necessary since we are already looking at the list before continuing)
#for n in range(0, len(new_followed)):
#    if new_followed[n][0] not in users_followed:
#        user_list.append(new_followed[n])

# Save list of followed users in a csv. In case it exist, append new information. Else, new file
try:
    user_list = user_list.append(list(new_followed))
except:
    user_list = pd.DataFrame(new_followed)
user_list.set_index(0).to_csv('user_list.csv', header=False)

print('Liked {} photos.'.format(likes))
print('Commented {} photos.'.format(comments))
print('Followed {} new people.'.format(followed))
