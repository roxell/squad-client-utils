#!/usr/bin/env python3

"""

Given a bad build, find the latest good one

"""


import re
from collections import defaultdict
from squad_client.core.models import Squad, ALL, Build
from squad_client.core.api import SquadApi
from squad_client.utils import first

getid = lambda s: re.search('\d+', s).group()


# Some configuration, might get parameterized later
SquadApi.configure('https://qa-reports.linaro.org')
squad = Squad()

group = squad.group('~anders.roxell')
project = group.project('lkft-linux-next-master')
bad_suite = project.suite('build')
bad_test = 'gcc-10-defconfig'

# sh environment on build next-20201210
#bad_build = project.build('next-20201210')
#bad_env = project.environment('sh')

# now with arm64 on build next-20201204
bad_build = project.build('next-20201204')
bad_env = project.environment('arm64')

# now with parisc on build next-20201124 (it should not return anything)
#bad_build = project.build('next-20201124')
#bad_env = project.environment('parisc')

print('Looking at the next good build in %s/%s for build %s' % (group.slug, project.slug, bad_build.version), flush=True)

tests = squad.tests(
    build__created_at__lt=bad_build.created_at,
    suite=bad_suite.id,
    environment=bad_env.id,
    metadata__name=bad_test,
    ordering='-build_id',
    result=True,
    count=1
)

if len(tests):
    test = first(tests)
    build = Build(getid(test.build))
    print('%s: https://qa-reports.linaro.org/%s/%s/build/%s' % (build.version, group.slug, project.slug, build.version))
else:
    print('No good build')
