import pytest
from bitbnspy import bitbns

def test_bibtbnsPlatform():
	bitbnsObj = bitbns('67F20A3E0DAD2875BFC0C91997E98023', '052AB687CB465042A78F17FDE0C87203')
	assert bitbnsObj.platformStatus()['code'] == 200