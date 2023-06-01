import requests
from dotenv import dotenv_values
from flask import Flask, render_template, request

app = Flask(__name__)
token = dotenv_values('.env')

#route to retrieve information as well as send updated info for processing
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        user_data = github_username(username)
        #call the repo stats function and return the information as a template for the stats.html page if user_data is valid. Return an error if the user data is not found
        if user_data:
            user_repo_stats = github_user_repo_stats(username)
            return render_template('stats.html', user_data = user_data, user_repo_stats = user_repo_stats)
        else:
            return render_template('error.html', msg="This user was not found.")
        
    return render_template('index.html')

#denote with f strings for convienence
def github_username(username):
    #user input for username
    url = f"https://api.github.com/users/{username}"
    headers = {'Authorization': f'Token {token["TOKEN"]}'}
    response = requests.get(url, headers = headers)
    

    #check if the response is valid(200 OK) and return that response in json form
    if response.status_code == 200:
        user_data = response.json()
        return user_data
    #if that user data is not found return nothing
    else:
        print("ERROR: Username invalid. Check spelling")
        return None
    
def github_user_repo_stats(username, forked=False):
    url = f"https://api.github.com/users/{username}/repos"
    headers = {'Authorization': f'Token {token["TOKEN"]}'}
    response = requests.get(url, headers = headers)

    #HTTP check if the response is valid
    if response.status_code == 200:
        repos = response.json()
        if not forked:
            forked_repos = []
            for repo in repos:
                if not repo['fork']:
                    forked_repos.append(repo)

        #find the needed stats
        repo_count = len(repos)
        stargazer_count = sum(repo.get('stargazer_count', 0) for repo in repos)
        fork_count = sum(repo.get('forks_count', 0) for repo in repos)
        avg_repo_size = sum([repo['size'] for repo in repos]) / len([repo['size'] for repo in repos])
        languages = {} #dictionary for languages

        #iterate through repos for to find languages
        for repo in repos:
            language = repo.get('language')
            
            #could have added another if statement here to check if language(s) in general is true or false
            #if a langauge is found increment our languages by 1
            if language:
                languages[language] = languages.get(language, 0) + 1

        #languages sorted, returned as a list of tuples that contain the key-value pairs from languages
        #starting from key specifies the sorting key for each tuple; lambda function is used to specify sorting based on the second element of the tuple (language count)
        sort_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True) #reverse=True means that the sorting is done from most used to least used based on count

        #return a dictionary containing the repo stats
        return {
            'repo_count': repo_count,
            'stargazer_count': stargazer_count,
            'fork_count': fork_count,
            'avg_repo_size': avg_repo_size,
            'languages': sort_languages
        }
    
    else:
        #if user data is not found return 404
        print(f"Data not found or failed to retrieve: {response.status_code}")
        return None

#user input
username = input("Enter a GitHub username: ")

#call the user_data from 'github_username' function with the username param
user_data = github_username(username)

#if the user data is valid print out the username and the appropriate repository stats
if user_data:
    print(f"Username: {user_data['login']}")
    print(f"Name: {user_data['name']}")
    print(f"Bio: {user_data['bio']}")
    print(f"Company: {user_data['company']}")
    print(f"Location: {user_data['location']}")
    # print(f"Website: {user_data['websiteUrl']}")
    # print(f"Social profiles: {user_data}['']")



    user_repo_stats = github_user_repo_stats(username)
    if user_repo_stats:
        #if stats are found print the number of repos, stargazers, and forks
        print(f"Total repos: {user_repo_stats['repo_count']}")
        print(f"Total stargazers: {user_repo_stats['stargazer_count']}")
        print(f"Total forks: {user_repo_stats['fork_count']}")

        #repo size (rounded to two decimals)
        avg_repo_size = user_repo_stats['avg_repo_size']

        #GB
        if avg_repo_size >= 1024**3:
            avg_repo_size = f"{avg_repo_size / (1024 ** 3):.2f} GB"

        #MB
        elif avg_repo_size >= 1024**2:
            avg_repo_size = f"{avg_repo_size / (1024 ** 2):.2f} MB"

        #KB
        elif avg_repo_size >= 1024:
            avg_repo_size = f"{avg_repo_size / 1024:.2f} KB"

        #could have added an else statement here to where I just return it as bytes if it's smaller than a kilobyte

        print(f"Average repo size: {avg_repo_size}")

        print("Languages: ")
        for language, count in user_repo_stats['languages']:
            print(f"{language}: {count}")

     

if __name__ == '__main__':
    app.run()