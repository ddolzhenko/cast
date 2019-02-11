rem @echo off
@echo Updating PyPi. Continue?
@pause
twine upload --repository pypi dist/* 
@pause
