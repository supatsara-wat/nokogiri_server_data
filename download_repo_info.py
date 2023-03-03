from regex import E
import requests
import json
import os
from tqdm import tqdm
import multiprocessing as mp
import time

URL_slack = "https://hooks.slack.com/services/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"
all_files = os.listdir('/mnt/ext-hdd1/github_repo_2023/repository_info')


def supercrawler(input_tuple, thread=1):
    with mp.Pool(thread) as p:
        multi_out = tqdm(p.imap(download_info, input_tuple,
                         chunksize=1), total=len(input_tuple))
        temp = [i for i in multi_out]
    return temp


def arrange_raw_data(data):
    arrange_data = dict()
    arrange_data['nameWithOwner'] = data['data']['repository']['nameWithOwner']
    arrange_data['description'] = data['data']['repository']['description']
    arrange_data['homepageUrl'] = data['data']['repository']['homepageUrl']
    arrange_data['url'] = data['data']['repository']['url']
    arrange_data['createdAt'] = data['data']['repository']['createdAt']
    arrange_data['updatedAt'] = data['data']['repository']['updatedAt']
    arrange_data['forkCount'] = data['data']['repository']['forkCount']
    arrange_data['isArchived'] = data['data']['repository']['isArchived']
    arrange_data['isFork'] = data['data']['repository']['isFork']
    arrange_data['licenseInfo'] = data['data']['repository']['licenseInfo']

    if len(data['data']['repository']['languages']['edges']) > 0:
        arrange_data['languages'] = dict()
        for lang in data['data']['repository']['languages']['edges']:
            arrange_data['languages'][lang['node']['name']] = lang['size']
    else:
        arrange_data['languages'] = None

    arrange_data['repositoryTopics'] = []
    for topic in data['data']['repository']['repositoryTopics']['edges']:
        arrange_data['repositoryTopics'].append(topic['node']['topic']['name'])

    arrange_data['labels'] = []
    for label in data['data']['repository']['labels']['edges']:
        arrange_data['labels'].append(label['node']['name'])

    arrange_data['stargazerCount'] = data['data']['repository']['stargazerCount']
    arrange_data['watchers'] = data['data']['repository']['watchers']['totalCount']
    arrange_data['issues'] = data['data']['repository']['issues']['totalCount']
    arrange_data['pullRequests'] = data['data']['repository']['pullRequests']['totalCount']
    arrange_data['releases'] = data['data']['repository']['releases']['totalCount']
    if data['data']['repository']['ref'] is not None:
        arrange_data['commits'] = data['data']['repository']['ref']['target']['history']['totalCount']
    else:
        arrange_data['commits'] = 0

    return arrange_data


def download_info(input_tuple):
    # Github personal access token
    tokens = ['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',
              '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', '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', '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']
    url = 'https://api.github.com/graphql'
    # Repository owner and name
    gh_index, file_name = input_tuple
    temp = file_name.split(':')

    if file_name+'.json' in all_files:
        return 1

    # GraphQL query
    query = """
query {
  repository(owner:"%s", name:"%s") {
    nameWithOwner
    description
    homepageUrl
    url
    createdAt
    updatedAt
    forkCount
    isArchived
    isFork
    licenseInfo {
      name
    }
    languages(first: 50, orderBy: {field: SIZE, direction: DESC}) {
      edges {
        size
        node {
          name
        }
      }
    }
    repositoryTopics(first: 50) {
      edges {
        node {
          topic {
            name
          }
        }
      }
    }
    labels(first: 50) {
      edges {
        node {
          name
        }
      }
    }
    stargazerCount
    watchers {
      totalCount
    }
    issues {
      totalCount
    }
    pullRequests {
      totalCount
    }
    releases {
      totalCount
    }
    forkCount
    ref(qualifiedName: "master") {
      target {
        ... on Commit {
          history {
            totalCount
          }
        }
      }
    }
  }
}
""" % (temp[0], temp[1])

    # Send a POST request with the GraphQL query
    headers = {'Authorization': 'Bearer %s' % tokens[gh_index]}

    max_retries = 5
    backoff = 3
    attempt = 0
    while True:
        try:
            response = requests.post(
                url, headers=headers, json={'query': query})
            # if ratelimit is not remain wait until rate limit reset and try again
            if 'X-RateLimit-Remaining' in response.headers:
                if int(response.headers['X-RateLimit-Remaining']) <= 0:
                    current_time = time.time()
                    left_time = current_time - \
                        int(response.headers['X-RateLimit-Reset'])
                    while(left_time < 0):
                        time.sleep(10)
                        current_time = time.time()
                        left_time = current_time - \
                            int(response.headers['X-RateLimit-Reset'])
                    response = requests.post(
                        url, headers=headers, json={'query': query})

            if response.status_code == 404:
                return 0

            data = json.loads(response.text)
            if data['data']['repository'] is None:
                return 0

            arrange_data = arrange_raw_data(data)
            with open('/mnt/ext-hdd1/github_repo_2023/repository_info/{}.json'.format(file_name), 'w') as outfile:
                json.dump(arrange_data, outfile, indent=4)
            return 1

        except Exception as e:
            attempt += 1
            if attempt == max_retries:
                print(e)
                requests.post(URL_slack, data=json.dumps(
                    {"text": "Error when downloading repository data: " + str(file_name) + "\n Log: " + str(e)}))
                return 0
            time.sleep(backoff)
            backoff += backoff


def get_repo_list():
    file_names = []
    gh_indexs = []
    f = open("/mnt/ext-hdd1/github_repo_2023/github_public_repo_list.json",
             "r")
    data = json.loads(f.read())
    count = 0
    smallest_index = 0
    largest_index = 10000000
    for repo in data:
        temp = data[repo]['full_name'].replace('/', ':')

        if count >= smallest_index and count <= largest_index:

            file_names.append(temp)

            if count % 4 == 0:
                gh_indexs.append(3)
            elif count % 4 == 1:
                gh_indexs.append(2)
            elif count % 4 == 2:
                gh_indexs.append(1)
            else:
                gh_indexs.append(0)

        count += 1

    f.close()
    print(len(gh_indexs), len(file_names))
    return list(zip(gh_indexs, file_names))


if __name__ == "__main__":

    input_tuple = get_repo_list()
    temp = supercrawler(input_tuple, thread=4)
    count = 0
    for i in temp:
        count = count+i
    print(len(input_tuple))
    print(count)
