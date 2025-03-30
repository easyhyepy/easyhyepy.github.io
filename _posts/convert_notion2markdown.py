
# import os
# import sys
# import shutil
# import re
# import datetime
# import urllib.parse
# import zipfile

# if len(sys.argv) != 2:
#     print("사용법: python convert_notion2markdown.py [노션 .zip 파일 경로]")
#     sys.exit(1)

# zip_path = sys.argv[1]

# if not zipfile.is_zipfile(zip_path):
#     print("오류: 유효한 .zip 파일이 아닙니다.")
#     sys.exit(1)

# # 압축 해제
# extracted_root = os.path.splitext(os.path.basename(zip_path))[0]
# extract_dir = f"unzipped_{extracted_root}"

# with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#     zip_ref.extractall(extract_dir)

# # 마크다운 파일 찾기
# md_files = [f for f in os.listdir(extract_dir) if f.endswith(".md")]
# if not md_files:
#     print("오류: 압축 안에 .md 파일이 없습니다.")
#     sys.exit(1)

# md_file = md_files[0]
# md_path = os.path.join(extract_dir, md_file)

# with open(md_path, "r", encoding="utf-8") as f:
#     content = f.read()

# # 제목 추출: 가장 첫 번째 "# " 헤더
# title_match = re.search(r'^# (.+)', content, re.MULTILINE)
# if title_match:
#     title_text = title_match.group(1).strip()
# else:
#     title_text = extracted_root  # fallback

# # 슬러그: 파일 이름과 이미지 폴더 이름으로 사용
# slug = re.sub(r'[^a-zA-Z0-9]+', '-', title_text).strip('-').lower()
# folder_name = slug

# # 이미지 저장 폴더 생성
# jekyll_img_dir = os.path.join("..", "images", folder_name)
# os.makedirs(jekyll_img_dir, exist_ok=True)

# # 이미지 복사
# image_exts = (".png", ".jpg", ".jpeg", ".webp")
# image_files = [f for f in os.listdir(extract_dir) if f.lower().endswith(image_exts)]
# for fname in image_files:
#     shutil.copy(os.path.join(extract_dir, fname), os.path.join(jekyll_img_dir, fname))

# # 이미지 경로 수정
# def replace_img_paths(match):
#     original_name = match.group(1)
#     encoded_name = urllib.parse.quote(original_name)
#     return f"![{original_name}](/images/{folder_name}/{encoded_name})"

# content = re.sub(r'!\[.*?\]\((.*?)\)', replace_img_paths, content)

# # YAML 헤더 추가
# date_prefix = datetime.date.today().isoformat()
# yaml_header = f"""---
# title: "{title_text}"
# date: {date_prefix}
# categories: [Security]
# tags: [CT]
# ---
# """

# # 마크다운 저장
# jekyll_post_dir = "."
# output_filename = f"{date_prefix}-{slug}.md"
# output_path = os.path.join(jekyll_post_dir, output_filename)

# with open(output_path, "w", encoding="utf-8") as f:
#     f.write(yaml_header + "\n" + content)

# print("변환 완료")
# print(f"제목: {title_text}")
# print(f"마크다운 파일: {output_path}")
# print(f"이미지 폴더: {jekyll_img_dir}")





import os
import sys
import shutil
import re
import datetime
import urllib.parse
import zipfile
from difflib import get_close_matches

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
if title_match:
    title_text = title_match.group(1).strip()
else:
    title_text = extracted_root

# 슬러그 및 이미지 폴더 이름
slug = re.sub(r'[^a-zA-Z0-9]+', '-', title_text).strip('-').lower()
folder_name = slug

# 이미지 저장 경로 생성
jekyll_img_dir = os.path.join("..", "images", folder_name)
os.makedirs(jekyll_img_dir, exist_ok=True)

# 이미지 파일 목록 확보
image_exts = (".png", ".jpg", ".jpeg", ".webp")
image_files = [f for f in os.listdir(extract_dir) if f.lower().endswith(image_exts)]

# 이미지 복사
for fname in image_files:
    shutil.copy(os.path.join(extract_dir, fname), os.path.join(jekyll_img_dir, fname))

# 마크다운 내 이미지 링크 추출
image_refs = re.findall(r'!\[.*?\]\((.*?)\)', content)

# 이미지 링크 경로 수정 (실제 파일명과 매칭)
for ref in image_refs:
    ref_unquoted = urllib.parse.unquote(os.path.basename(ref))
    match = get_close_matches(ref_unquoted, image_files, n=1)
    if match:
        actual_name = match[0]
        encoded_name = urllib.parse.quote(actual_name)
        content = content.replace(f'({ref})', f'(/images/{folder_name}/{encoded_name})')
    else:
        print(f"[경고] '{ref}'에 해당하는 이미지 파일을 찾을 수 없습니다.")


# 본문에서 첫 번째 헤더 제거: 중복내용이라;;
content = re.sub(r'^# .+\n+', '', content, count=1, flags=re.MULTILINE)

# YAML 헤더 추가
date_prefix = datetime.date.today().isoformat()
yaml_header = f"""---
title: "{title_text}"
date: {date_prefix}
categories: [Security]
tags: [CT]
---
"""

# 마크다운 저장
jekyll_post_dir = "."
output_filename = f"{date_prefix}-{slug}.md"
output_path = os.path.join(jekyll_post_dir, output_filename)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(yaml_header + "\n" + content)

# zip과 압축 해제 폴더 삭제
try:
    os.remove(zip_path)
    shutil.rmtree(extract_dir)
except Exception as e:
    print(f"[경고] 파일 정리 중 오류 발생: {e}")

print("변환 완료")
print(f"제목: {title_text}")
print(f"마크다운 파일: {output_path}")
print(f"이미지 폴더: {jekyll_img_dir}")


# 작업 디렉토리 내 Zone.Identifier 파일 정리
for fname in os.listdir('.'):
    if fname.endswith(':Zone.Identifier') or 'Zone.Identifier' in fname:
        try:
            os.remove(fname)
            print(f"삭제됨: {fname}")
        except Exception as e:
            print(f"삭제 실패: {fname} → {e}")
