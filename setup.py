from setuptools import setup, find_packages

setup(
    name='nonebot_plugin_ygo',
    version="1.0.1",
    description=(
        'nonebot的游戏王卡查插件'
    ),
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='anlen123',
    author_email='1761512493@qq.com',
    maintainer='anlen123',
    maintainer_email='1761512493@qq.com',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/anlen123/nonebot_plugin_ygo',
    install_requires=[
        'aiohttp',
        'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
        'nonebot2>=2.0.0-beta.1,<3.0.0',
    ]
)
