#!/usr/bin/env python3
import requests
import json
from urllib.parse import quote_plus
import sys
import os
import time
import subprocess

QUERIES_JSON = os.getenv("QUERIES_JSON") # array of queries like ["query1", "query2", ..]
# output dir
OUTPUT_DIR = "output"
WEBHOOK = os.getenv("WEBHOOK")

if not os.path.exists(OUTPUT_DIR):
	os.mkdir(OUTPUT_DIR)


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
	print("GITHUB_TOKEN not set! might bump into issues.")

def search_repos(q):
	# url encode query for safety
	q_encoded = quote_plus(q)

	results = []
	if not GITHUB_TOKEN:
		headers = {"Accept": "application/vnd.github.text-match+json", "X-GitHub-Api-Version": "2022-11-28"}
	else:
		headers = {"Accept": "application/vnd.github.text-match+json", "Authorization":f"Bearer {GITHUB_TOKEN}", "X-GitHub-Api-Version": "2022-11-28"}
	
	sort_orders = ['sort=updated&order=desc','sort=stars&order=desc', 'sort=forks&order=desc', 'sort=help-wanted-issues&order=desc', 'sort=updated&order=asc', 'sort=stars&order=asc', 'sort=forks&order=asc', 'sort=help-wanted-issues&order=asc']
	print("sorting by updated desc..")
	for sort_order in sort_orders:
		print(f'======== sort order: {sort_order} =======')
		page = 1
		while True:
			try:
				print(f'==== getting page {page}, with {sort_order} ====')
				r = requests.get(f"https://api.github.com/search/repositories?per_page=1000&{sort_order}&page={page}&q="+q_encoded, headers=headers)
				if r.status_code != 200:
					print("bad status:", r.status_code, r.text)

				d = r.json()
			
				total_count = d['total_count']
				results.extend(d['items'])
				if len(results) >= total_count:
					break
				page += 1
			except Exception as e:
				print('error, breaking:', e)
				break

	return results

queries = json.loads(QUERIES_JSON)

total_found = 0

for q in queries:
	results = search_repos(q)
	found_repos = set()
	for item in results:
		found_repos.add(item['html_url'])

	query_repos_txt_path = os.path.join(OUTPUT_DIR, quote_plus(q)) + ".txt"
	with open(query_repos_txt_path, 'w') as f:
		for repo in found_repos:
			total_found += 1
			f.write(repo + "\n")

	print(f"found {len(found_repos)} unique repos for query {q}")
	try:
		if len(found_repos) > 0:
			r = requests.post(WEBHOOK, headers={"Content-Type":"application/json"}, data={"content":f"found {len(found_repos)} unique repos for query {q}"})
			if r.status_code != 200:
				print("Bad webhook status code:", r.status_code)
	except Exception as e:
		print("error posting to webhook:",e)


