import requests
import json
import os

# Github personal access token
token = ''

# GraphQL API endpoint
url = 'https://api.github.com/graphql'

# Repository owner and name
owner = "Alfincahyaputra"
name = "http-ikenley.com"

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
    isArchived
    isFork
    isPrivate
    forkCount
    stargazerCount
    repositoryTopics(first: 100) {
      edges {
        node {
          topic {
            name
          }
        }
      }
    }
    languages(first: 100, orderBy: {field: SIZE, direction: DESC}) {
      edges {
        size
        node {
          name
        }
      }
    }
    labels(first: 100) {
      edges {
        node {
          name
        }
      }
    }
    licenseInfo {
      name
    }
    primaryLanguage {
      name
    }
    stargazers {
      totalCount
    }
    watchers {
      totalCount
    }
    issues {
      totalCount
    }
    pullRequests {
      totalCount
    }
    forks {
      totalCount
    }
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
""" % (owner, name)

# Send a POST request with the GraphQL query
headers = {'Authorization': 'Bearer %s' % token}
response = requests.post(url, headers=headers, json={'query': query})

# Parse the response
if response.status_code == 200:
    data = json.loads(response.text)
    repository = data['data']['repository']
    print(repository)
else:
    print("Failed to get repository information. Status code: %s" %
          response.status_code)
