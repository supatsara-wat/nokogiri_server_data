import requests
import os
import json
from tqdm import tqdm
import multiprocessing as mp
import time

URL_slack = "https://hooks.slack.com/services/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"


def supercrawler(input_tuple, thread=1):
    with mp.Pool(thread) as p:
        multi_out = tqdm(p.imap(get_readme, input_tuple,
                         chunksize=1), total=len(input_tuple))
        temp = [i for i in multi_out]
    return temp


def get_readme(input_tuple):
    url, file_name = input_tuple
    # if file_name+'.diff' in os.listdir(outputsource):
    # return 1
    max_retries = 5
    backoff = 3
    attempt = 0
    while True:
        try:
            response = requests.get(url)
            time.sleep(1)
            if response.status_code == 404:
                return 0
            with open('/mnt/ext-hdd1/github_repo_2023/README/{}'.format(file_name), 'w') as f:
                f.write(response.text)
            return 1

        except Exception as e:
            attempt += 1
            if attempt == max_retries:
                print(e)
                requests.post(URL_slack, data=json.dumps(
                    {"text": "Error when downloading " + str(url) + " Log: " + str(e)}))
                return 0
            time.sleep(backoff)
            backoff += backoff


def get_repo_list():
    urls = []
    file_names = []
    f = open("/mnt/ext-hdd1/github_repo_2023/github_public_repo_list.json",
             "r")
    data = json.loads(f.read())
    count = 0
    smallest_index = 0
    largest_index = 10000000
    for repo in data:
        master_url = 'https://raw.githubusercontent.com/{}/master/README.md'.format(
            data[repo]['full_name'])
        temp = data[repo]['full_name'].replace('/', ':')

        if count >= smallest_index and count <= largest_index:
            urls.append(master_url)

            file_names.append(temp + '.md')

        count += 1

    f.close()
    print(len(urls), len(file_names))
    return list(zip(urls, file_names))


if __name__ == "__main__":

    input_tuple = get_repo_list()
    temp = supercrawler(input_tuple, thread=8)
    count = 0
    for i in temp:
        count = count+i
    print(len(input_tuple))
    print(count)
