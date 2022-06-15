from glob import glob
from subprocess import run
from typing import IO
import os


class Pandoc:

  def __init__(self, src_file_path: str, dst_file_path: str) -> None:
    self.cmd = ['pandoc']
    self.src_file_path = src_file_path
    self.dst_file_path = dst_file_path

  def build(self) -> list[str]:
    self.cmd.append(self.src_file_path)
    self.flag('-o', self.dst_file_path)
    return self.cmd

  def flag(self, name: str, value=None):
    self.cmd.append(name)
    if value is not None:
      self.cmd.append(value)


def get_document_title(path: str) -> str:
  with open(path) as f:
    return f.readline().replace('# ', '').replace('\n', '')


def main() -> IO:

  template_dir_name = 'templates'
  template_dir_path = os.path.join('.', template_dir_name)

  index_template_file_name = 'index-template.html'
  index_template_file_path = os.path.join(template_dir_path, index_template_file_name)

  public_dir_name = 'public'
  public_dir_path = os.path.join('.', public_dir_name)

  index_file_name = 'index.html'
  index_file_path = os.path.join(public_dir_path, index_file_name)

  posts_dir_name = 'posts'
  posts_dir_path = os.path.join(public_dir_path, posts_dir_name)

  src_dir_name = 'src'
  src_dir_path = os.path.join('.', src_dir_name)
  src_files_glob = os.path.join(src_dir_path, '*.md')

  if not os.path.exists(public_dir_path):
    os.mkdir(public_dir_path)

  if not os.path.exists(posts_dir_path):
    os.mkdir(posts_dir_path)

  post_anchor_list = []

  for src_file_path in glob(src_files_glob):

    title = get_document_title(src_file_path)
    src_file_name = os.path.basename(src_file_path)
    dst_file_name = src_file_name.replace('.md', '.html')
    dst_file_path = os.path.join(posts_dir_path, dst_file_name)

    p = Pandoc(src_file_path, dst_file_path)
    p.flag('-f', 'markdown')
    p.flag('-t', 'html')
    p.flag('-s')
    p.flag('--toc')
    p.flag('-M', f'title={title}')
    p.flag('--template', 'templates/post-template.html')
    cmd = p.build()

    run(cmd)

    if not os.path.exists(dst_file_path):
      print(f'Could not build {dst_file_path}')
      print('Exiting!')
      exit(1)

    href = os.path.join('.', posts_dir_name, dst_file_name)
    anchor = f'<a href="{href}">{title}</a>'
    post_anchor_list.append(anchor)

  anchor_str = '<br/>\n'.join(post_anchor_list)

  with open(index_template_file_path, 'r') as index_template_file:
    index_template_file_content = index_template_file.read()
    index_file_content = index_template_file_content.replace('$POST_LIST$', anchor_str)
    with open(index_file_path, 'w') as index_file:
      index_file.write(index_file_content)


if __name__ == "__main__":
  main()
