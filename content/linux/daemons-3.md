Title: Daemons: Criando e controlando serviços (parte 3)
Date: 2016-06-11 13:35
Tags: linux, c, daemons, servers
Slug: daemons-3
Category: Linux
Summary: 
Status: Draft

Nos artigos anteriores, [Daemons: Introdução (parte 1)]({filename}daemons.md) e [Daemons: Pidfiles e daemons de única instância (parte 2)]({filename}daemons-2.md), mostramos de forma geral como funcionam os _daemons_. Nós até criamos uma função em C capaz de criar um daemon e outra capaz de criar um arquivo de lock (_pidfile_).

Neste post, vamos mostrar como usar alguns mecanismos do Linux para facilitar a criação e o controle de daemons, como o comando `service` e os _SysV Init scripts_.

Criar, iniciar e parar um daemon, dentre outras operações, são coisas tão comuns em sistemas operacionais que eles quase sempre provêem mecanismos para simplificar estas tarefas. São estes mecanismos que iremos ver aqui.

Para entender este artigo, um conhecimento prévio sobre daemons é necessário. Mas não é nada de tão complicado. Caso você queira, você pode dar uma lida nos artigos publicados anteriormente:

- [Daemons: Introdução (parte 1)]({filename}daemons.md);
[Daemons: Pidfiles e daemons de única instância (parte 2)]({filename}daemons-2.md).

Serviços, runlevel e o SysV Init
--------------------------------

Conforme foi explicado no primeiro artigo desta série de posts ([Daemons: Introdução (parte 1)]({filename}daemons.md)), um daemon é um tipo de programa muito comum em ambientes _Unix like_. A imensa maioria destes daemons podem ser controlados pelo sistema ou pelo administrador do sistema (isto é, podem ser iniciados, parados, reiniciados, etc).

No Linux, um **Serviço** (ou _service_) é, basicamente, um daemon que provê uma funcionalidade e que pode ser controlado pelo sistema ou pelo administrador (iniciado e parado). Estas funcionalidades podem ser entregar um recurso a um usuário sob demanda (como no caso do [Apache](https://en.wikipedia.org/wiki/Apache_HTTP_Server)) ou simplismente realizar uma tarefa específica continuamente (como no caso do [Cron](https://en.wikipedia.org/wiki/Cron)). O primeiro tipo de serviço que mostramos (que entregam recursos sob demanda) são também chamados de servidores.

No dia-a-dia, manipular serviços (iniciar, parar e recarregar) é algo muito comum. Além disso, vários serviços são necessários para o correto funcionamento de uma máquina e devem estar presentes desde a hora do boot do sistema. Poder controlar estes serviços de forma correta e padronizada, acionando-os corretamente no momento oportuno, vários esquemas de boot e de controle de serviços foram implementados ao longo do tempo. O [**SysV Init**](https://en.wikipedia.org/wiki/Init#SysV-style), também chamado de System V ou SysV, é um destes esquemas.

O SysV Init é um esquema clássico e razoavelmente antigo, implementado inicialmente no sistema operacional _System V_ (ou _SysV_), da AT&T. Entretanto, ele é um esquema que ainda hoje é usado em muitas distribuições Linux, apesar de estar sendo gradativamente migrado para modelos mais novos (como o [Systemd](https://en.wikipedia.org/wiki/Systemd)).

**Obs:** Os termos System V e SysV não deixam claro se estamos falando do sistema operacional ou do modelo de iniciação. Por isso, adotamos a nomenclatura SysV Init para evitar confusões.

Um conceito interessante existente no SysV Init é o [**Runlevel**](https://en.wikipedia.org/wiki/Runlevel). Um runlevel é um modo padrão de operação de um sistema operacional. Normalmente, os sistemas operacionais possuem 7 runlevels, numerados de 0 à 6. A medida que o número que representa um runlevel aumenta, a quantidade de serviços que o sistema operacional ativa durante o boot vai aumentando (à excessão do runlevel 6, que indica um reboot do computador). O runlevel 1, por exemplo, permite apenas um único usuário logado no sistema e deixa a imensa maioria dos serviços inativos (ele é parecido com o _Safe Mode_ do Windows). Já no dia-a-dia, um servidor típico roda em um runlevel maior ou igual a 2.

Assim, para que possamos iniciar um daemon durante o boot, temos que fazer duas coisas: a primeira é preparar e registrar nosso daemon como um serviço (para que o sistema operacional possa controlá-lo), e a segunda é registrá-lo nos runlevels apropriados.

### Criando e controlando serviços no SysV Init

Para registrar um serviço em um sistema operacional que utiliza o modelo SysV Init, temos que criar um script de controle de serviço, chamado de **SysV Init script**.

Estes scripts possuem permissão de execução e aceitam um argumento que representa a ação de controle que deve tomada. As mais comuns são `start`, `stop` e `restart` (que são obrigatórias para este tipo de script), além das ações `status` e `reload` (que não são abrigatórias, mas são muito comuns). Na maioria das distribuições, ficam no diretório `/etc/init.d`.

Como exemplo, no servidor Ubuntu 14.04 LTS de teste que estou usando para criar os exemplos deste artigo, existem vários scripts SysV Init. Vou mostrar alguns:

```console
$ ls /etc/init.d
acpid          dbus               networking  rsync              umountnfs.sh
anacron        dns-clean          ondemand    rsyslog            umountroot
[...]
```

Para podermos demontrar como funcionam estes scripts, vamos usar o daemon que criamos no artigo anterior como base. O código fonte dele pode ser visto [aqui](/daemons/#criando-um-daemon), e o nome dele é `gb_daemon`.

Daqui em diante, vamos partir do princípio que já o compilamos (vide artigo anterior) e que estamos usando o usuário `root`.

Primeiramente, vamos copiá-lo para o diretório `/usr/local/bin`:

```console
$ cp gb_daemon /usr/local/bin
```

Vamos, agora, criar uma primeira versão do nosso script de serviço em `/etc/init.d/gb-daemon`:

```bash
#!/bin/sh

GB_DAEMON="gb_daemon"
COMMAND="/usr/local/bin/$GB_DAEMON"

case "$1" in
    start)
        "$COMMAND"
        echo "GB daemon started"
        ;;
    stop)
        killall "$GB_DAEMON"
        echo "GB daemon stopped"
        ;;
    restart|reload)
		killall "$GB_DAEMON"
		echo "GB daemon stopped"
		"$COMMAND"
		echo "GB daemon started"
		;;
    status)
        if ps -C "$GB_DAEMON" >/dev/null; then
            echo "GB daemon is running"
        else
            echo "GB daemon is not running"
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 <start|stop|restart|reload|status>"
        ;;
esac
```

Agora, só falta dar permissão de execução neste script:

```console
$ chmod +x /etc/init.d/gb-daemon
```

Vamos, agora, iniciar nosso daemon e nos certificar que ele está rodando:

```console
$ /etc/init.d/gb-daemon start
GB daemon started
$ /etc/init.d/gb-daemon status
GB daemon is running
$ ps aux | grep gb_daemon | grep -v grep
root      3259  0.0  0.0   4320   428 ?        S    22:09   0:00 /usr/local/bin/gb_daemon
```

Por fim, vamos parar o nosso daemon (verificando depois que ele, de fato, parou):

```console
$ /etc/init.d/gb-daemon stop
GB daemon stopped
$ /etc/init.d/gb-daemon status
GB daemon is not running
$ ps aux | grep gb_daemon | grep -v grep
```

Essa nossa primeira versão usa uma implementação bem simples. O objetivo é mostrar a ideia geral por trás desses scripts sem entrar em detalhes mais complexos.

Algumas considerações sobre a nossa implementação:

- Ela roda o comando `/usr/local/bin/gb_daemon` para iniciar o serviço;
    - Uma vez que o nosso programa `gb_daemon` por si só já se transforma em daemon durante a inicialização, apenas rodar o comando já é o suficiente para iniciar corretamente o serviço;
    - Perceba que o nosso comando `start` possui a limitação de não conferir se um progresso `gb_daemon` já foi iniciado, permitindo inicializar vários daemons se o rodarmos várias vezes;
    - O correto seria que o comando `start` criasse apenas um único daemon, não inicializando novos processos caso um daemon iniciado anterior pelo mesmo comando `start` estivesse rodando;
- Ela utiliza o comando `killall gb_daemon` para parar o daemon (enviando para ele um `SIGHUP`);
    - Essa é uma implementação bem limitada, visto que podemos ter vários processos rodando no sistema chamados `gb_daemon` (programas diferentes do nosso, mas que por coincidência usasse o mesmo nome), ou mesmo podemos ter iniciado manualmente (sem usarmos o Sysv Init script para este fim), e todos esses programas seriam finalizados;
    - O correto seria que o comando `stop` do nosso script finalizasse apenas o daemon que ele mesmo iniciou no comando `start`;
- Ela utiliza o comando `ps -C gb_daemon` para verificar se o nosso serviço está ou não rodando;
    - Perceba que, caso nós tenhamos vários processos rodando no sistema chamados `gb_daemon`, ou mesmo caso existisse um `gb_daemon` iniciado manualmente, o nosso `status` iria dizer que o nosso serviço está rodando;
    - O correto seria que o comando `status` indicasse se um daemon iniciado pelo nosso script estivesse rodando (ignorando outros processos iniciados de outras formas);
- Ela utiliza o comando `killall gb_daemon` seguido de um `/usr/local/bin/gb_daemon` para reiniciar o serviço;
	- Além de possuir as mesmas limitações já apresentadas para os serviços `stop` e `start`, o nosso `restart` possui código duplicado, fazendo com que qualquer programador que se preze sinta calafrios (a menos que este seja adepto a ["metodologia" de programação Go Horse](http://www.mochilabinaria.com.br/metodo-de-desenvolvimento-ghp-esqueca-tudo-o-que-voce-aprendeu/) :));
- Sempre que algo dá errado (quando não conseguimos iniciar o daemon ao rodar `start`, ou quando o daemon já não estava rodando quando damos `stop`), o nosso programa não retorna um código de erro apropriado.

Por estes e outros problemas (acredite, existem mais problemas), esta implementação não é recomendada para uso em produção. Mais para frente, vamos mostrar scripts melhores.

A maioria das distribuições Linux possui o comando [`service`](http://linux.die.net/man/8/service). Em resumo, esse comando procura e roda o SysV Init script correspondente. Ou seja, também podemos rodar:

```console
$ service gb-daemon start
GB daemon started
$ service gb-daemon stop
GB daemon stopped
```

**Obs:** No Ubuntu, o comando `service` faz ainda mais coisas. Por exemplo, além de subir os scripts do SysV Init, ele pode subir outros tipos de serviços (como serviços do Upstart ou do Systemd). Ainda não hora de falar desses outros tipos de serviços, mas fica a dica de usar o comando `service` no dia-a-dia ao invés de usar diretamente os scripts em `/etc/init.d`, visto que o `service` é mais geral e pode ser usados com outros tipos de serviços.

### Registrando serviços do Sysv Init no boot do sistema

Bem, já aprendemos como criar um SysV Init script. Entretanto, colocar um SysV Init script no diretório `/etc/init.d` apenas faz com que o Linux conheça o serviço (serviço registrado), mas não permite ao SysV Init saber em que runlevels e em que ordem este script deverá subir durante o boot.

Para isso, devemos criar um [link simbólico](https://en.wikipedia.org/wiki/Symbolic_link) deste script em um diretório do tipo `/etc/rcN.d`, onde `N` é o número de um runlevel.

Como exemplo, no servidor Ubuntu de testes que estou usando, temos os seguintes serviços registrados para subir em runlevel 2:

```console
$ ls /etc/rc2.d/
README         S20speech-dispatcher  S35vboxadd-service  S70pppd-dns     S99rc.local
S20kerneloops  S30vboxadd            S50saned            S99grub-common
S20rsync       S30vboxadd-x11        S70dns-clean        S99ondemand
```

E para ver que eles são realmente links simbólicos:

```console
$ ls -lh /etc/rc2.d/S20rsync
lrwxrwxrwx 1 root root 15 Ago  7  2015 /etc/rc2.d/S20rsync -> ../init.d/rsync
```

Estes links simbólicos devem começar com a letra `K` (indicando que ele não deve subir neste runlevel) ou `S` (indicando que o sistema deve subí-lo neste runlevel). Os scripts que começam com a letra `K`, embora não sejam necessários durante o boot do sistema, são importantes quando o sistema muda entre runlevels para saber quais serviços devem subir e quais devem ser desativados.

Já os números que vem depois da primeira letra (20, no caso do nosso serviço `rsync`), são usados para ordenar os serviços, para o sistema saber quais serviços devem subir antes e quais devem subir depois.

Agora vamos registrar o nosso serviço para subir no boot do sistema. No caso do meu Ubuntu de testes, podemos usar o comando `update-rc.d`:

```console
$ update-rc.d gb-daemon defaults
```

**Obs:** Por ora, vamos ignorar os warning que o comando vai gerar. Como falei, o nosso script inicial é muito simples, tão simples que o `update-rc.d` reclama. Vamos resolver isso mais para frente.

Ao rodar este comando com o parâmetro `defaults`, links simbólicos são criados de forma com que o nosso daemon suba nos runlevels de 2 a 5, ficando desativado nos demais (incluindo o runlevel 1).

Para conferir:

```console
$ ls -lh /etc/rc2.d/ | grep gb-daemon
lrwxrwxrwx 1 root root  19 Jul  9 23:56 S20gb-daemon -> ../init.d/gb-daemon
```

Mais informações sobre os conceitos discutidos até aqui podem ser encontrados [neste artigo do site _The Linux Fundation_](https://www.linux.com/news/introduction-services-runlevels-and-rcd-scripts), e [neste artigo no site _Ubuntu Help_](https://help.ubuntu.com/community/UbuntuBootupHowto#Traditional_Sysvinit_and_Before_Ubuntu_6.10).

### Um exemplo: o serviço Nginx

Vamos instalar um servidor [Nginx](https://nginx.org/en/) no nosso Ubuntu de testes:

```console
$ apt-get install nginx
```

Depois de fazermos isso, podemos ver que um script de inicialização e controle do Nginx foi criado em `/etc/init.d/nginx`:

```console
$ ls /etc/init.d/nginx
/etc/init.d/nginx
```

Vamos usar este script para manipular o serviço:

```console
$ service nginx status
 * nginx is running
$ service nginx restart
 * Restarting nginx nginx                                                         [ OK ]
$ service nginx stop
$ service nginx status
 * nginx is not running
```

Também podemos verificar que o Nginx está registrado para subir no boot no runlevel 2 (embora não esteja configurado para subir no runlevel 1):

```console
$ ls /etc/rc1.d/ | grep nginx
K20nginx
$ ls /etc/rc2.d/ | grep nginx
S20nginx
```

Ah, além dos comandos que já mostramos anteriormente, o serviço do Nginx possui implementando vários outros comandos:

```console
$ service nginx
Usage: nginx {start|stop|restart|reload|force-reload|status|configtest|rotate|upgrade}
```

Por exemplo, o comando `configtest` pode ser usado para saber se o arquivo de configuração atual do daemon é válido ou possui algum erro:

```console
$ service nginx configtest
 * Testing nginx configuration                                                    [ OK ]
```

Mais sobre scripts do SysV Init
-------------------------------



Referências
-----------

https://www.linux.com/news/introduction-services-runlevels-and-rcd-scripts
https://help.ubuntu.com/community/UbuntuBootupHowto