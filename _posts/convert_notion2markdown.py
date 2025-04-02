import os
import sys
import shutil
import re
import datetime
import urllib.parse
import zipfile
from difflib import get_close_matches
from sklearn.feature_extraction.text import TfidfVectorizer

def extract_tags_tfidf(text, top_n=2):
    # 너무 짧은 줄 제거
    sentences = [line for line in text.split('\n') if len(line.split()) > 2]
    docs = [" ".join(sentences)]
    vectorizer = TfidfVectorizer(stop_words='english', max_features=50)
    tfidf_matrix = vectorizer.fit_transform(docs)
    scores = zip(vectorizer.get_feature_names_out(), tfidf_matrix.toarray()[0])
    sorted_terms = sorted(scores, key=lambda x: x[1], reverse=True)
    return [term for term, score in sorted_terms[:top_n]]

def convert_inline_math_to_block(content):
    return re.sub(r'\$(.+?)\$', lambda m: f"$$ {m.group(1)} $$", content)

if len(sys.argv) != 2:
    print("사용법: python convert_notion2markdown.py [노션 .zip 파일 경로]")
    sys.exit(1)

zip_path = sys.argv[1]

if not zipfile.is_zipfile(zip_path):
    print("오류: 유효한 .zip 파일이 아닙니다.")
    sys.exit(1)

# 압축 해제
extracted_root = os.path.splitext(os.path.basename(zip_path))[0]
extract_dir = f"unzipped_{extracted_root}"

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

# 마크다운 파일 찾기
md_files = [f for f in os.listdir(extract_dir) if f.endswith(".md")]
if not md_files:
    print("오류: 압축 안에 .md 파일이 없습니다.")
    sys.exit(1)

md_file = md_files[0]
md_path = os.path.join(extract_dir, md_file)

with open(md_path, "r", encoding="utf-8") as f:
    content = f.read()

# 제목 추출
title_match = re.search(r'^# (.+)', content, re.MULTILINE)
title_text = title_match.group(1).strip() if title_match else extracted_root

# 슬러그 및 이미지 폴더 이름
slug = re.sub(r'[^a-zA-Z0-9]+', '-', title_text).strip('-').lower()
folder_name = slug

# 이미지 저장 경로 생성
jekyll_img_dir = os.path.join("..", "images", folder_name)
os.makedirs(jekyll_img_dir, exist_ok=True)

# 이미지 파일 목록 확보 및 복사
image_exts = (".png", ".jpg", ".jpeg", ".webp")
image_files = [f for f in os.listdir(extract_dir) if f.lower().endswith(image_exts)]
for fname in image_files:
    shutil.copy(os.path.join(extract_dir, fname), os.path.join(jekyll_img_dir, fname))

# 이미지 링크 경로 수정
image_refs = re.findall(r'!\[.*?\]\((.*?)\)', content)
for ref in image_refs:
    ref_unquoted = urllib.parse.unquote(os.path.basename(ref))
    match = get_close_matches(ref_unquoted, image_files, n=1)
    if match:
        actual_name = match[0]
        encoded_name = urllib.parse.quote(actual_name)
        content = content.replace(f'({ref})', f'(/images/{folder_name}/{encoded_name})')
    else:
        print(f"[경고] '{ref}'에 해당하는 이미지 파일을 찾을 수 없습니다.")

# 헤더 제거 + 수식 변환
content = re.sub(r'^# .+\n+', '', content, count=1, flags=re.MULTILINE)
content = convert_inline_math_to_block(content)

# 태그 추출
tags = extract_tags_tfidf(content)

# YAML 헤더 생성
date_prefix = datetime.date.today().isoformat()
yaml_header = f"""---
title: "{title_text}"
date: {date_prefix}
categories: [Security]
tags: [{', '.join(tags)}]
mathjax: true
---"""

# 마크다운 저장
jekyll_post_dir = "."
output_filename = f"{date_prefix}-{slug}.md"
output_path = os.path.join(jekyll_post_dir, output_filename)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(yaml_header + "\n" + content)

# zip 및 압축해제 폴더 삭제
try:
    os.remove(zip_path)
    shutil.rmtree(extract_dir)
except Exception as e:
    print(f"[경고] 파일 정리 중 오류 발생: {e}")

# Zone.Identifier 파일 제거
for fname in os.listdir('.'):
    if fname.endswith(':Zone.Identifier') or 'Zone.Identifier' in fname:
        try:
            os.remove(fname)
            print(f"삭제됨: {fname}")
        except Exception as e:
            print(f"삭제 실패: {fname} → {e}")

print("변환 완료")
print(f"제목: {title_text}")
print(f"마크다운 파일: {output_path}")
print(f"이미지 폴더: {jekyll_img_dir}")
