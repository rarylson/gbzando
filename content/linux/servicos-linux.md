Title: Serviços no Linux: Criando e controlando serviços via init.d (parte 1)
Date: 2016-06-11 13:35
Tags: linux, c, daemons, servers
Slug: servicos-linux
Category: Linux
Summary: 
Status: Draft

Em artigos anteriores publicados neste blog, [Daemons: Introdução (parte 1)]({filename}daemons.md) e [Daemons: Pidfiles e daemons de única instância (parte 2)]({filename}daemons-2.md), mostramos de forma geral como funcionam os _daemons_.

Neste post, vamos mostrar como usar alguns mecanismos do Linux para facilitar a criação e o controle de daemons, como o comando `service` e os _SysV Init scripts_.

Criar, iniciar e parar um daemon, dentre outras operações, são coisas tão comuns em sistemas operacionais que eles quase sempre provêem mecanismos para simplificar estas tarefas. São estes mecanismos que iremos ver aqui.

Para entender este artigo, um conhecimento prévio sobre daemons é necessário. Mas não é nada de tão complicado. Caso você queira, você pode dar uma lida nos artigos publicados anteriormente:

- [Daemons: Introdução (parte 1)]({filename}daemons.md);
- [Daemons: Pidfiles e daemons de única instância (parte 2)]({filename}daemons-2.md).

Serviços, runlevel e o SysV Init
--------------------------------

Conforme foi explicado no primeiro artigo desta série de posts ([Daemons: Introdução (parte 1)]({filename}daemons.md)), um daemon é um tipo de programa muito comum em ambientes _Unix like_. A imensa maioria destes daemons podem ser controlados pelo sistema ou pelo administrador do sistema (isto é, podem ser iniciados, parados, reiniciados, etc).

No Linux, um **Serviço** (ou _service_) é, basicamente, um daemon que provê uma funcionalidade e que pode ser controlado pelo sistema ou pelo administrador (iniciado e parado). Estas funcionalidades podem ser entregar um recurso a um usuário sob demanda (como no caso do [Apache](https://en.wikipedia.org/wiki/Apache_HTTP_Server)) ou simplismente realizar uma tarefa específica continuamente (como no caso do [Cron](https://en.wikipedia.org/wiki/Cron)). O primeiro tipo de serviço que mostramos (que entregam recursos sob demanda) são também chamados de servidores.

No dia-a-dia, manipular serviços (iniciar, parar e recarregar) é algo muito comum. Além disso, vários serviços são necessários para o correto funcionamento de uma máquina e devem estar presentes desde a hora do boot do sistema. Para poder controlar estes serviços de forma correta e padronizada, acionando-os corretamente no momento oportuno, vários esquemas de boot e de controle de serviços foram implementados ao longo do tempo. O [**SysV Init**](https://en.wikipedia.org/wiki/Init#SysV-style), também chamado de System V ou SysV, é um destes esquemas.

O SysV Init é um esquema clássico e razoavelmente antigo, implementado inicialmente no sistema operacional _System V_ (ou _SysV_), da AT&T. Entretanto, ele é um esquema que ainda hoje é usado em muitas distribuições Linux, apesar de estar sendo gradativamente migrado para modelos mais novos (como o [Systemd](https://en.wikipedia.org/wiki/Systemd)).

**Obs:** Os termos System V e SysV não deixam claro se estamos falando do sistema operacional ou do modelo de iniciação. Por isso, adotamos a nomenclatura SysV Init para evitar confusões.

Um conceito interessante existente no SysV Init é o [**Runlevel**](https://en.wikipedia.org/wiki/Runlevel). Um runlevel é um modo padrão de operação de um sistema operacional. Normalmente, os sistemas operacionais possuem 7 runlevels, numerados de 0 à 6. A medida que o número que representa um runlevel aumenta, a quantidade de serviços que o sistema operacional ativa durante o boot vai aumentando (à excessão do runlevel 6, que indica um reboot do computador). O runlevel 1, por exemplo, permite apenas um único usuário logado no sistema e deixa a imensa maioria dos serviços inativos (ele é parecido com o _Safe Mode_ do Windows). Já no dia-a-dia, um servidor típico roda em um runlevel maior ou igual a 2, onde um número maior de serviços são ativados durante o boot do sistema.

Assim, para que possamos iniciar um daemon durante o boot, temos que fazer duas coisas: a primeira é preparar e registrar nosso daemon como um serviço (para que o sistema operacional possa controlá-lo), e a segunda é registrá-lo nos runlevels apropriados.

### Criando e controlando serviços no SysV Init

Para registrar um serviço em um sistema operacional que utiliza o modelo SysV Init, temos que criar um script de controle de serviço, chamado de **SysV Init script**.

Estes scripts possuem permissão de execução e aceitam um argumento que representa a ação de controle que deve ser tomada. Na maioria das distribuições, ficam no diretório `/etc/init.d`.

Os comandos mais comuns que usados em um SysV Init script são os seguintes:

- `start`: Iniciar o serviço;
- `stop`: Parar o serviço;
- `restart`: Reiniciar o serviço (parar e depois iniciar novamente o serviço);
- `status`: Verificar se o serviço está ou não rodando;
- `reload`: Recarregar a configuração do serviço (carregar uma nova configuração sem precisar parar o serviço, _on the fly_);
- `force-reload`: Caso o serviço permita sua reconfiguração _on the fly_, recarregá-lo (_reload_). Caso contrário, reiniciar o serviço (_restart_).

Como exemplo, no servidor Ubuntu 14.04 LTS de teste que usamos para criar os exemplos deste artigo, existem vários scripts SysV Init. Vamos mostrar alguns:

```console
$ ls /etc/init.d
acpid          dbus               networking  rsync              umountnfs.sh
anacron        dns-clean          ondemand    rsyslog            umountroot
[...]
```

Para podermos demontrar como funcionam estes scripts, vamos usar o daemon que criamos no último artigo sobre daemon como base. O código fonte dele pode ser visto [aqui](/daemons-2/#criando-pidfiles), e o nome dele é `gb_daemon`.

Daqui em diante, vamos partir do princípio que já o compilamos (conforme apresentado no artigo) e que estamos usando o usuário `root`.

Primeiramente, vamos copiá-lo para o diretório `/usr/local/bin`:

```console
$ cp gb_daemon /usr/local/bin
```

Vamos, agora, criar uma primeira versão do nosso script de serviço em `/etc/init.d/gb_daemon_service`:

```
#!sh
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
    restart|force-reload)
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
        fi
        ;;
    *)
        echo "Usage: $0 <start|stop|restart|force-reload|status>"
        ;;
esac
```

Agora, só falta dar permissão de execução neste script:

```console
$ chmod +x /etc/init.d/gb_daemon_service
```

Vamos, agora, iniciar nosso daemon e nos certificar que ele está rodando:

```console
$ /etc/init.d/gb_daemon_service start
GB daemon started
$ /etc/init.d/gb_daemon_service status
GB daemon is running
$ ps aux | grep gb_daemon | grep -v grep
root      3259  0.0  0.0   4320   428 ?        S    22:09   0:00 /usr/local/bin/gb_daemon
```

Por fim, vamos parar o nosso daemon (verificando depois que ele, de fato, parou):

```console
$ /etc/init.d/gb_daemon_service stop
GB daemon stopped
$ /etc/init.d/gb_daemon_servive status
GB daemon is not running
$ ps aux | grep gb_daemon | grep -v grep
```

Essa nossa primeira versão usa uma implementação bem simples. O objetivo é apenas mostrar a ideia geral por trás desses scripts, apresentando alguns conceitos básicos, sem entrar em detalhes mais complexos.

Algumas considerações sobre a nossa implementação:

- Rodamos o comando `/usr/local/bin/gb_daemon` para iniciar o serviço;
    - Uma vez que o nosso programa `gb_daemon` por si só já se transforma em daemon durante a inicialização, apenas rodar o comando já é o suficiente para iniciar corretamente o serviço;
    - Perceba que o nosso comando `start` possui a limitação de não conferir se um progresso `gb_daemon` já foi iniciado antes de tentar iniciar um novo daemon;
    - Em muitos casos, isso pode fazer com que mais de um daemon seja iniciado ao mesmo tempo no sistema;
    - No nosso caso, como o próprio daemon `gb_daemon` verifica se alguma instância sua já foi iniciada (veja a nossa implementação no artigo anterior), isso não ocorre. Mesmo assim, o comando `start` não sabe que o daemon que ele tentou iniciar finalizou em seguida (ele acha que o daemon foi inicializado com sucesso);
    - O correto seria que o comando `start` apenas tentasse iniciar um daemon caso nenhuma instância estivesse rodando. Caso contrário, ele deveria informar ao administrador que o serviço já estava rodando e que não foi preciso iniciar um novo;
- Utilizamos o comando `killall gb_daemon` para parar o daemon (enviando para ele um `SIGHUP`);
    - Essa implementação possui uma grande limitação. Caso tenhamos vários processos rodando no sistema também chamados de `gb_daemon` (programas diferentes do nosso, mas que por coincidência usem o mesmo nome), ou caso tenhamos iniciado mais de uma instância do nosso daemon de propósito (casa um com um PID diferente), todos esses programas seriam finalizados;
    - Justamente por causa da limitação acima é que o nosso script de inicialização de serviço se chama `gb_daemon_service`, e não apenas `gb_daemon`, para não termos dois processos diferentes com o mesmo nome);
    - O correto seria que o comando `stop` do nosso script finalizasse apenas o daemon que ele mesmo iniciou no comando `start`, e informasse ao administrador caso o serviço já estive parado e que não foi necessário encerrar nenhum processo;
- Utilizamos o comando `ps -C gb_daemon` para verificar se o nosso serviço está ou não rodando;
    - Perceba que, caso tenhamos vários processos rodando no sistema, diferentes do nosso daemon, mas também chamados `gb_daemon` (caso já apresentado anteriormente no comando `stop`), o nosso `status` iria dizer que o nosso serviço está rodando;
    - Este foi outro motivo para chamarmos o nosso script de inicialização de `gb_daemon_service`, e não simplesmente `gb_daemon`;
    - O correto seria que o comando `status` informasse ao administrador se um daemon iniciado pelo nosso script está ou não rodando (ignorando outros processos iniciados de outras formas);
- Chamados, em sequência, os comandos `killall gb_daemon` e `/usr/local/bin/gb_daemon` para reiniciar o serviço;
	- Além de possuir as mesmas limitações já apresentadas para os serviços `stop` e `start`, o nosso `restart` possui código duplicado, fazendo com que qualquer programador que se preze sinta calafrios (a menos que ele seja adepto a ["metodologia" de programação Go Horse](http://www.mochilabinaria.com.br/metodo-de-desenvolvimento-ghp-esqueca-tudo-o-que-voce-aprendeu/) :));
- Perceba que, sempre que algo dá errado (quando não conseguimos iniciar o daemon ao rodar `start` porque um outro daemon já está rodando, ou quando o daemon já estava parado ao rodar `stop`), o nosso programa não informa de forma apropriada o administrador do sistema.

Por estes e outros problemas (acredite, existem mais problemas), esta implementação não é recomendada para uso em produção. Mais para frente, vamos mostrar scripts melhores.

A maioria das distribuições Linux possui o comando [`service`](http://linux.die.net/man/8/service). Em resumo, esse comando procura e roda o SysV Init script correspondente. Ou seja, também podemos rodar:

```console
$ service gb_daemon_service start
GB daemon started
$ service gb_daemon_service stop
GB daemon stopped
```

**Obs:** No Ubuntu, o comando `service` faz ainda mais coisas. Por exemplo, além de subir os scripts do SysV Init, ele pode subir outros tipos de serviços (como serviços do Upstart ou do Systemd). Ainda não é hora de falar desses outros tipos de serviços (vamos falar mais sobre eles em outro artigo), mas fica a dica de usar o comando `service` no dia-a-dia ao invés de usar diretamente os scripts em `/etc/init.d`, visto que o `service` é mais geral e pode ser usados com outros tipos de serviços.

### Registrando serviços do Sysv Init no boot do sistema

Bem, já aprendemos como criar um SysV Init script. Entretanto, colocar um SysV Init script no diretório `/etc/init.d` apenas faz com que o Linux conheça o serviço (serviço registrado), mas não permite ao SysV Init saber em que runlevels e em que ordem este script deverá subir durante o boot.

Para isso, devemos criar um [link simbólico](https://en.wikipedia.org/wiki/Symbolic_link) deste script em um diretório do tipo `/etc/rcN.d`, onde `N` é o número de um runlevel.

Como exemplo, no servidor Ubuntu de testes que estamos usando, temos os seguintes serviços registrados para subir em runlevel 2:

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
$ update-rc.d gb_daemon_service defaults
```

**Obs:** Por ora, vamos ignorar os _warnings_ que o comando vai gerar. Como falei, o nosso script inicial é muito simples, tão simples que o `update-rc.d` reclama. Vamos resolver isso mais para frente.

Ao rodar este comando com o parâmetro `defaults`, links simbólicos são criados de forma com que o nosso daemon suba nos runlevels de 2 a 5, ficando desativado nos demais (incluindo o runlevel 1).

Para conferir:

```console
$ ls -lh /etc/rc2.d/ | grep gb_daemon_service
lrwxrwxrwx 1 root root  19 Jul  9 23:56 S20gb_daemon_service -> ../init.d/gb_daemon_service
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

Scripts do SysV Init melhores
-----------------------------

O script de SysV Init que criamos na sessão anterior, conforme já falado, era apenas um exemplo simples, conceitual, e que apresenta vários problemas.

Vamos, agora, criar scripts SysV Init melhores, bons para uso em produção e sem os vários problemas mostrados anteriormente. Vamos fazer isso em 2 etapas: inicialmente, vamos criar um script mais manual, onde iremos implementar várias melhorias importantes; depois, vamos reusar alguns recursos do Ubuntu para simplificar e padronizar melhor o nosso script.

### Criando scripts SysV Init melhores

Vamos, agora, criar uma segunda versão do nosso script de serviço (init script). Ele será melhor e mais completa que a sua versão anterior e, como vamos corrigir algumas limitações que ele possui, vamos poder mudar seu nome de `/etc/init.d/gb_daemon_service` para simplesmente `/etc/init.d/gb_daemon`.

Assim, vamos primeiro apagar quaisquer resquícios do script anterior:

```console
$ rm /etc/init.d/gb_daemon_service
$ rm rc*.d/*gb_daemon_service
```

E criar o nosso novo init script, agora em `/etc/init.d/gb_daemon`:

```
#!sh
#!/bin/sh

GB_DAEMON="gb_daemon"
PID="/run/$GB_DAEMON.pid"
COMMAND="/usr/local/bin/$GB_DAEMON"

[ -x "$COMMAND" ] || exit 0

do_start () {
    do_status >/dev/null && return 1
    "$COMMAND"
    sleep 0.1
    echo "GB daemon started"
}

do_stop() {
    do_status >/dev/null || return 1
    kill $(cat "$PID")
    sleep 0.1
    echo "GB daemon stopped"
}

do_status() {
    if [ -f "$PID" ]; then
        echo "GB daemon is running"
        return 0
    else
        echo "GB daemon is not running"
        return 1
    fi
}

case "$1" in
    start)
        do_start || exit 1
        ;;
    stop)
        do_stop || exit 1
        ;;
    restart|force-reload)
        do_stop
        do_start || exit 1
        ;;
    status)
        do_status || exit 1
        ;;
    *)
        echo "Usage: $0 <start|stop|restart|force-reload|status>"
        ;;
esac
```

Vamos nos concentrar nas novidades:

- Antes de tudo, verificamos se o arquivo do nosso `gb_daemon` realmente existe e é executável (a instrução `[ -x "$COMMAND" ]` faz isso para a gente). Caso contrário, entendemos que o nosso daemon não está instalado e não fazemos nada, apenas retornando;
    - Essa é uma prática comum, que evita erros no caso de uma aplicação ser desinstalada, mas o SysV Init script dela não ser removido;
- A nossa implementação faz uso de funções. Elas são as funções `do_start`, `do_stop` e `do_status`;
    - Além de deixar o nosso código mais organizado, usar funções permite a reutilização de código;
    - Por exemplo, o comando `restart` (e também o `force-reload`) chama a função `do_stop` e, em seguida, a `do_start`, reaproveitando o código. Outro exemplo são as funções `do_start` e `do_stop`, que chamam a função `do_status` em sua implementação;
- Sempre quando algo der errado, estamos retornando o _exit code_ 1 para informar apropriadamente o administrador ou o sistema;
    - Além disso, neste caso, nenhuma mensagem de sucesso é erradamente impressa na tela;
- A função `do_status` verifica se o _pidfile_ do nosso daemon existe ou não (a instrução `[ -f "$PID" ]` faz isso). Caso o pidfile exista, ela considera que o serviço está rodando. Do contrário, ela conclui que o serviço não está rodando;
    - Essa função retorna 0 se o serviço estiver rodando e 1 caso contrário;
- A função `do_stop` usa o comando `kill` para enviar um sinal para o processo adequado, extraindo o PID deste processo de acordo com o valor encontrado no pidfile (comando `cat "$PID"`);
- A função `do_start` verifica se o serviço já está rodando antes de tentar executá-lo. De forma semelhante, a função `do_stop` verifica se o serviço já está parado. Caso estes casos de excessão ocorram, estas funções retornam 1 para indicar que algo deu errado;
- Após rodar o comando que inicializa o serviço (em `do_start`) ou após enviar um sinal para o término do serviço (em `do_stop`), nós esperamos 0.1 segundos antes de retornar (`sleep 0.1`);
    - No caso de `do_start`, nós fazemos isto porque, quando o comando que cria o daemon retorna (o daemon se coloca em _background_, logo após seu primeiro _fork_), o pidfile ainda não estará criado, sendo somente criado um pouquinho depois. Durante esse curto intervalo de tempo, estaríamos sugeitos a uma condição de corrida. Assim, usamos um `sleep` para garantir que `do_start` apenas retorne depois do nosso pidfile ter sido escrito;
    - No caso de `do_stop`, ocorre coisa parecida: demora um tempo desde o momento que o comando `kill` retorna e o momento em que o pidfile é, de fato, removido.

Vamos registrar o nosso novo daemon para inicializar no boot do sistema:

```console
$ update-rc.d gb_daemon defaults
```

**Obs:** Assim como fizemos anteriormente, vamos continuar ignorando os warnings que o comando vai gerar.

E testá-lo, verificando que ele se comporta muito melhor nos casos de excessão:

```console
$ service gb_daemon start
GB daemon started
$ echo $?
0
$ service gb_daemon status
GB daemon is running
$ echo $?
0
$ service gb_daemon start
$ echo $?
1
$ service gb_daemon restart
GB daemon stopped
GB daemon started
$ service gb_daemon stop
GB daemon stopped
$ echo $?
0
$ service gb_daemon status
GB daemon is not running
$ echo $?
1
$ service gb_daemon stop
$ echo $?
1
```

Opa, bem melhor...

Mesmo com todos esses avanços, o nosso script ainda tem algumas limitações.

A primeira delas é que a função `sleep` pode não ser a melhor maneira


- Sleep é ruim
- Stale pidfile

### Criando scripts SysV Init melhores ainda



Referências
-----------

https://www.linux.com/news/introduction-services-runlevels-and-rcd-scripts
https://help.ubuntu.com/community/UbuntuBootupHowto
https://www.digitalocean.com/community/tutorials/how-to-configure-a-linux-service-to-start-automatically-after-a-crash-or-reboot-part-2-reference
https://wiki.debian.org/LSBInitScripts
https://refspecs.linuxbase.org/LSB_3.0.0/LSB-PDA/LSB-PDA/iniscrptact.html