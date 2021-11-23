# squad-jobs

Jobs involving [`squad`](https://github.com/Linaro/squad) that are not implemented in [`squad-client`](https://github.com/Linaro/squad-client) or [`squad-report`](https://gitlab.com/Linaro/lkft/reports/squad-report).

## Usage

### `squad-list-changes`: Get all of the changes for a build, compared to a base build.

```
❯ pipenv run ./squad-list-changes -h
usage: squad-list-changes [-h] --group GROUP --project PROJECT --build BUILD --base-build BASE_BUILD

List all changes for a squad build, compared to a base build

optional arguments:
  -h, --help            show this help message and exit
  --group GROUP         squad group
  --project PROJECT     squad project
  --build BUILD         squad build
  --base-build BASE_BUILD
                        squad build to compare to
```

#### Comparing a build to itself should return zero changes.

```
❯ pipenv run ./squad-list-changes --group=lkft --project=linux-next-master-sanity --build=next-20211020 --base-build=next-20211020
[]
```

#### Given a collection of changes, get a subset that contains only the regressions

```
❯ pipenv run ./squad-list-changes --group=lkft --project=linux-next-master-sanity --build=next-20211020 --base-build=next-20211019 > changes.json

❯ jq '.[] | select(.change=="regression")' changes.json
```

### `squad-list-results`: Get all of the results for a build

```
❯ pipenv run ./squad-list-results -h
usage: squad-list-results [-h] --group GROUP --project PROJECT --build BUILD

List all results for a squad build

optional arguments:
  -h, --help         show this help message and exit
  --group GROUP      squad group
  --project PROJECT  squad project
  --build BUILD      squad build
```

#### Given a collection of results, get a subset that contains only failures

```
❯ pipenv run ./squad-list-results --group=lkft --project=linux-next-master-sanity --build=next-20211022 > results.json

❯ jq '.[] | select(.status=="fail")' results.json
```

#### `squad-list-failures`: If a build has a lot of tests, filter with the http request instead

```python
filters = {
    "has_known_issues": False,
    "result": False,
}
tests = build.tests(count=ALL, **filters).values()
```

```
❯ pipenv run ./squad-list-failures -h
usage: squad-list-failures [-h] --group GROUP --project PROJECT --build BUILD

List all results for a squad build

optional arguments:
  -h, --help         show this help message and exit
  --group GROUP      squad group
  --project PROJECT  squad project
  --build BUILD      squad build
```

### `squad-list-result-history`: Get all of the results for a test, starting with this build

```
❯ pipenv run ./squad-list-result-history -h
usage: squad-list-result-history [-h] --group GROUP --project PROJECT --build BUILD --environment ENVIRONMENT --suite SUITE --test TEST

List the result history of a test

optional arguments:
  -h, --help            show this help message and exit
  --group GROUP         squad group
  --project PROJECT     squad project
  --build BUILD         squad build
  --environment ENVIRONMENT
                        squad environment
  --suite SUITE         squad suite
  --test TEST           squad test
```

## Contributing

This (alpha) project is managed on [`github`](https://github.com) at https://github.com/Linaro/squad-client-utils

Open an issue at https://github.com/Linaro/squad-client-utils/issues

Open a pull request at https://github.com/Linaro/squad-client-utils/pulls

For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://github.com/Linaro/squad-client-utils/blob/master/LICENSE)
