import os
import re
import argparse
import random
import logging
from urllib.parse import urlparse, parse_qs

# تنظیم لاگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_random_filename(prefix, extension, length=4):
    random_number = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    return f"{prefix}{random_number}.{extension}"

def read_lines_from_file(filepath):
    with open(filepath, 'r') as file:
        return [line.strip() for line in file]

def extract_domains(urls):
    domains = set()
    for url in urls:
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        domains.add(domain)
    return domains

def filter_urls_by_param_type(urls):
    numeric_param_urls = set()
    non_numeric_param_urls = set()

    for url in urls:
        query_params = parse_qs(urlparse(url).query)
        has_numeric = False
        has_non_numeric = False
        for values in query_params.values():
            for value in values:
                if re.match(r'^\d+$', value):
                    has_numeric = True
                else:
                    has_non_numeric = True

        if has_numeric:
            numeric_param_urls.add(url)
        if has_non_numeric:
            non_numeric_param_urls.add(url)
    
    return numeric_param_urls, non_numeric_param_urls

def find_similar_urls(urls):
    similarity_map = {}
    for url in urls:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.path.split('/')[-1]}?{parsed_url.query}"
        if base_url in similarity_map:
            similarity_map[base_url].append(url)
        else:
            similarity_map[base_url] = [url]

    return similarity_map

def filter_urls_by_sensitive_words(urls, sensitive_words):
    sen_urls = {word: [] for word in sensitive_words}

    for url in urls:
        for word in sensitive_words:
            if word in url:
                sen_urls[word].append(url)
    
    return sen_urls

def main(input_file):
    urls = read_lines_from_file(input_file)
    sensitive_words = read_lines_from_file('sen.txt')
    
    output_dir = generate_random_filename('res', '', 4)
    os.makedirs(output_dir, exist_ok=True)

    numeric_param_urls, non_numeric_param_urls = filter_urls_by_param_type(urls)
    
    with open(os.path.join(output_dir, 'numparams.txt'), 'w') as file:
        for url in numeric_param_urls:
            file.write(url + '\n')

    with open(os.path.join(output_dir, 'nonnumparams.txt'), 'w') as file:
        for url in non_numeric_param_urls:
            file.write(url + '\n')
    
    domains = extract_domains(urls)
    with open(os.path.join(output_dir, 'domains.txt'), 'w') as file:
        for domain in domains:
            file.write(domain + '\n')
    
    similarity_map = find_similar_urls(urls)
    same_dir = os.path.join(output_dir, 'sames')
    os.makedirs(same_dir, exist_ok=True)
    
    for i, similar_urls in enumerate(similarity_map.values(), start=1):
        if len(similar_urls) > 1:
            with open(os.path.join(same_dir, generate_random_filename('same', 'txt', 4)), 'w') as file:
                for url in similar_urls:
                    file.write(url + '\n')
    
    sen_urls = filter_urls_by_sensitive_words(urls, sensitive_words)
    sen_dir = os.path.join(output_dir, 'sen')
    os.makedirs(sen_dir, exist_ok=True)

    for word, matched_urls in sen_urls.items():
        if matched_urls:
            with open(os.path.join(sen_dir, f"{word}.txt"), 'w') as file:
                for url in matched_urls:
                    file.write(url + '\n')

    logging.info(f"Output written to directory: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process URLs from a file.")
    parser.add_argument("--file", "-f", required=True, help="Input file containing URLs")
    args = parser.parse_args()

    main(args.file)
