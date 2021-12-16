[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4063720.svg)](https://doi.org/10.5281/zenodo.4063720)

# F-UJI (FAIRsFAIR Research Data Object Assessment Service)
Developers:[Robert Huber](mailto:rhuber@marum.de), [Anusuriya Devaraju](mailto:anusuriya.devaraju@googlemail.com)

[![Publish Docker image](https://github.com/pangaea-data-publisher/fuji/actions/workflows/publish-docker.yml/badge.svg)](https://github.com/pangaea-data-publisher/fuji/actions/workflows/publish-docker.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4063720.svg)](https://doi.org/10.5281/zenodo.4063720)


## Overview

F-UJI is a web service to programatically assess FAIRness of research data objects based on [metrics](https://doi.org/10.5281/zenodo.3775793) developed by the [FAIRsFAIR](https://www.fairsfair.eu/) project. 
The service will be applied to demostrate the evaluation of objects in repositories selected for in-depth collaboration with the project.  

The '__F__' stands for FAIR (of course) and '__UJI__' means 'Test' in Malay. So __F-UJI__ is a FAIR testing tool.

**Cite as**

Devaraju, A. and Huber, R. (2021). An automated solution for measuring the progress toward FAIR research data. Patterns, vol 2(11), https://doi.org/10.1016/j.patter.2021.100370

### Clients and User Interface

A web demo using F-UJI is available at https://www.f-uji.net

An R client package that was generated from the F-UJI OpenAPI definition is available from https://github.com/NFDI4Chem/rfuji.

## Assessment Scope, Constraint and Limitation
The service is **in development** and its assessment depends on several factors. 
- In the FAIR ecosystem, FAIR assessment must go beyond the object itself. FAIR enabling services and repositories are vital to ensure that research data objects remain FAIR over time. Importantly, machine-readable services (e.g., registries) and documents (e.g., policies) are required to enable automated tests. 
- In addition to repository and services requirements, automated testing depends on clear machine assessable criteria. Some aspects (rich, plurality, accurate, relevant) specified in FAIR principles still require human mediation and interpretation. 
- The tests must focus on generally applicable data/metadata characteristics until domain/community-driven criteria have been agreed (e.g., appropriate schemas and required elements for usage/access control, etc.). For example, for some of the metrics (i.e., on I and R principles), the automated tests we proposed only inspect the ‘surface’ of criteria to be evaluated. Therefore, tests are designed in consideration of generic cross-domain metadata standards such as dublin core, dcat, datacite, schema.org, etc.
- FAIR assessment is performed based on aggregated metadata; this includes metadata embedded in the data (landing) page, metadata retrieved from a PID provider (e.g., Datacite content negotiation) and other services (e.g., re3data).

![alt text](https://github.com/pangaea-data-publisher/fuji/blob/master/fuji_server/static/main.png?raw=true)

## Requirements
Python 3.5.2+

### 308 redirects
In order to deal with 308 redirects, the following patch has to be applied on urrlib:
https://github.com/python/cpython/pull/19588/commits

### Google Dataset Search
* Download the latest Dataset Search corpus file from: https://www.kaggle.com/googleai/dataset-search-metadata-for-datasets
* Open file fuji_server/helper/create_google_cache_db.py and set variable 'google_file_location' according to the file location of the corpus file
* Run create_google_cache_db.py which creates a SQLite database in the data directory.

The service was generated by the [swagger-codegen](https://github.com/swagger-api/swagger-codegen) project. By using the
[OpenAPI-Spec](https://github.com/swagger-api/swagger-core/wiki) from a remote server, you can easily generate a server stub.  
The service uses the [Connexion](https://github.com/zalando/connexion) library on top of Flask.

## Usage
Before running the service, please set user details in the config file, see config/server.ini.

To install F-UJI, you may execute the following python-based or docker-based installation commands from the root directory:

### Python module-based installation:

From the fuji source folder run
```bash
pip3 install .
```
or to install the last fixed dependencies
```
pip3 install .
```
The F-uji server can now be started with.
```
python3 -m fuji_server -c fuji_server/config/server.ini
```
Alternative you can install the latest F-UJI release on PyPI
```bash
pip3 install fuji
```
you can also use poetry
```bash
poetry install fuji
```

### Docker-based installation:

```bash
docker run -d -p 1071:1071 ghcr.io/pangaea-data-publisher/fuji
```

To access the Swagger  user interface, open the url below on the browser:

```
http://localhost:1071/fuji/api/v1/ui/
```

Your Swagger definition lives here:

```
http://localhost:1071/fuji/api/v1/swagger.json
```

You can provide a different server config file this way:

```bash
docker run -d -p 1071:1071 -v server.ini:/usr/src/app/fuji_server/config/server.ini ghcr.io/pangaea-data-publisher/fuji
```

You can also build the docker image from the source code:

```bash
docker build -t <tag_name> .
docker run -d -p 1071:1071 <tag_name>
```

### Notes

To avoid tika startup warning message, set environment variable TIKA_LOG_PATH. For more information, see [https://github.com/chrismattmann/tika-python](https://github.com/chrismattmann/tika-python)

If you receive the exception 'urllib2.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] on MacOS, run the install command shipped with Python :
./Install\ Certificates.command


## License
This project is licensed under the MIT License; for more details, see the [LICENSE](https://github.com/pangaea-data-publisher/fuji/blob/master/LICENSE) file.


## Acknowledgements

F-UJI is a result of the [FAIRsFAIR](https://www.fairsfair.eu/) “Fostering FAIR Data Practices In Europe” project which received funding from the European Union’s Horizon 2020 project call H2020-INFRAEOSC-2018-2020 (grant agreement 831558).

The project was also supported through our contributors by the [Helmholtz Metadata Collaboration (HMC)](https://www.helmholtz-metadaten.de/en), an incubator-platform of the Helmholtz Association within the framework of the Information and Data Science strategic initiative.
