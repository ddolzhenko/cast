rem @echo off
@echo Updating TEST PyPi. Continue?
@pause
twine upload --repository testpypi dist/*
@pause
