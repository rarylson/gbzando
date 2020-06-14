GBzando
=======

Blog about Computing: cloud, infrastructure, programming and network.

This project contains both the blog engine source code (theme and plugins) and the blog content (articles).

Althought the blog engine source code is written in English, the blog content is written in Portuguese (`pt_BR`).

How it works?
-------------

This project was developed using [Pelican](https://github.com/getpelican/pelican/), a static site generator written in Python.

The articles are written in [Markdown](http://daringfireball.net/projects/markdown/). Themes are written in [Jinja2](http://jinja.pocoo.org).

Install
-------

In Ubuntu:

```sh
pip install -r requirements.txt
brew install optipng
# On Ubuntu, run:
#   apt install optipng libjpeg8
```

Usage
-----

To run the local development server:

```sh
make devserver
```

To stop de local development server:

```sh
make stopserver
```

To publish the blog:

```sh
# Generate config file
# Edit 'deploy_config.py' after.
cp deploy_config.py.sample deploy_config.py
# Generate files to publish
make html_publish
# Publish
invoke publish
```

License
-------

The software is released under the [Revised BSD License](LICENSE).

The articles are released under the [Creative Commons Attribution-NonCommercial License](http://creativecommons.org/licenses/by-nc/3.0/deed.en_US).

TODO
----

### Blog engine

- Neighbors
	- See: https://github.com/getpelican/pelican-plugins/tree/master/neighbors
- Code block: Line numbers in CSS instead of in HTML
- Admonition:
	- See: https://python-markdown.github.io/extensions/admonition/
- Increase default font size

### Articles

**Note:** Articles titles are in Portuguese.

**Sistemas operacionais:**

- Serviços no Linux: Criando e controlando serviços via Systemd (parte 3)
- Serviços no Linux: Exemplo real (parte 4)
    - Exemplo: Ordem dos serviços no boot - MySQL + ISCSI
- Como um servidor atende múltiplos clientes: Introdução (parte 1)
- Como um servidor atende múltiplos clientes: Arquiteturas baseadas em fork (parte 2)
- Como um servidor atende múltiplos clientes: Gerenciando número de workers (parte 3)
- Como um servidor atende múltiplos clientes: Arquiteturas baseadas em event loop (parte 4)
- Paralelizando workloads em CPUs multi-core: Introdução (parte 1)
- Paralelizando workloads em CPUs multi-core: Exemplo real (parte 2)
    - Compactando vários arquivos em GZIP
- Troubleshooting no Linux: Introdução (parte 1)
- Troubleshooting no Linux: CPU (parte 2)
- Troubleshooting no Linux: Storage (parte 3)
    - Incluir filesystem (disk space)
- Troubleshooting no Linux: Exemplo real - Storage no RDS (parte 4)
- Troubleshooting no Linux: Memória (parte 5)
- Troubleshooting no Linux: Network (parte 6)

**Redes:**

- Usando estatística e percentis no monitoramento
- Latência ICMP na AWS: Primeiras medições (parte 1)
- Latência ICMP na AWS: Alguns mitos e verdades sobre CDN (CloudFront) (parte 2)

**Sistemas operacionais / AWS:**

- Backups e restores: Conceitos iniciais (parte 1)
- Backups e restores: Bancos de dados (parte 2)
- Backups e restores: RPO, RTO e porquê importam (parte 3)
- Backups e restores: EBS (parte 4)
- Backups e restores: RDS (parte 5)

**Redes / AWS:**

- Latência em aplicações web: Conceitos de TCP e TLS (parte 1)
- Latência em aplicações web: Conceitos de HTTP (parte 2)
- Latência em aplicações web: Medindo latências HTTP na AWS (parte 3)
- Latência em aplicações web: Conceitos de Keepalive (parte 4)
- Latência em aplicações web: Conceitos de CDN (parte 5)
- Latência em aplicações web: Otimizando latências HTTP na AWS usando o CloudFront (parte 6)
- Latência em aplicações web: Mais otimizações na AWS (parte 7)
- Latência em aplicações web: Synthetic Monitoring e Real User Monitoring (parte 8)

**Sistemas distribuidos:**

- Conceitos de sistemas distribuídos: Introdução (parte 1)
    - HA, Fault tolerance, scalability e elasticity
- Conceitos de sistemas distribuídos: Probabilidade (parte 2)
- Conceitos de sistemas distribuídos: Concensus over quorum (parte 3)
- Conceitos de sistemas distribuídos: Retry (parte 4)

**AWS:**

- Modelo de responsabilidade compartilhada na AWS: Introdução (parte 1)
- Modelo de responsabilidade compartilhada na AWS: O caso do RDS (parte 2)

**Banco da dados / AWS:**

- RDS: Conceitos básicos que geralmente passam despercebidos (parte 1)
- RDS: Usuários root e master (parte 2)
- RDS: Escolhendo a storage mais adequada (parte 3)
- RDS: Multi-AZ (parte 4)
- RDS: Vertical scaling com Multi-AZ (parte 5)
    - Incluir o que a aplicação deve e não deve fazer
- RDS: Stop/start (parte 6)
- RDS: Manutenção e upgrades (parte 7)
- RDS: Parameter groups (parte 8)
    - Incluir parâmetros default, e como eles ajudam na gerência do uso de memória
- Replicação master/slave no MySQL: Introdução (parte 1)
- Replicação master/slave no MySQL: Durabilidade e consistência de transações (parte 2)
- Replicação master/slave no MySQL: Aprofundando (parte 3)
- Read Replicas no RDS: Introdução (parte 1)
    - Incluir "How is a read replica created?"
- Read Replicas no RDS: Casos de uso (parte 2)
- Read Replicas no RDS: Alguns mitos e verdades (parte 3)
- Gerência de memória no MySQL: Introdução (parte 1)
- Gerência de memória no MySQL: Aumentando o max connections no RDS (parte 2)
- RDS Performance Insights: Introdução (parte 1)
- RDS Performance Insights: Exemplos (parte 2)
- RDS Performance Insights: Counters e Query Statistics (parte 3)
- RDS Performance Insights: Mais exemplos (parte 4)
