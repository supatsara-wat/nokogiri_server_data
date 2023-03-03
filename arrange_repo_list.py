import os
from tqdm import tqdm
import json

all_repos = dict()
all_files = os.listdir(
    '/mnt/ext-hdd1/github_repo_2023')
for file in tqdm(all_files):
    f = open("/mnt/ext-hdd1/github_repo_2023/{}".format(file),
             "r")
    data = json.loads(f.read())
    for repo in data:
        all_repos[repo] = data[repo]

with open('/mnt/ext-hdd1/github_repo_2023/github_public_repo_list.json', 'w') as outfile:
    json.dump(all_repos, outfile, indent=4)

print(len(all_repos))
