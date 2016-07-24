Title: Daemons: Pidfiles e daemons de única instância (parte 2)
Date: 2016-07-24 15:00
Tags: linux, c, daemons
Slug: daemons-2
Category: Linux
Summary: Neste artigo, mostramos porque muitos daemons só podem ter uma única instância rodando no sistema. Mostramos o que são pidfiles e como eles funcionam. Também vamos implementar uma função em C capaz de criar um pidfile de forma atômica.

No artigo anterior, [Daemons: Introdução (parte 1)]({filename}daemons.md), mostramos de forma geral como funcionam os _daemons_. Nós até implementamos uma função em C capaz de criar um daemon.

Uma preocupação comum ao executar um daemon é garantir que apenas uma instância do daemon esteja rodando no sistema. Muitos daemons são desenvolvidos para controlar e manipular um determinado conjunto de recursos de forma exclusiva. Rodar várias instâncias dele ao mesmo tempo pode levar a inúmeros problemas.

Neste post, vamos mostrar o uso de _pidfile_ para garantir que apenas uma instância de um daemon execute no sistema. Seguindo com a nossa mania de mostrar exemplos práticos, iremos mostrar uma implementação desta técnica em C. Vamos também mostrar exemplos reais de daemons que usam esta técnica.

Para entender este artigo, um conhecimento prévio sobre daemons é necessário. Talvez vala a pena dar uma lida no artigo anterior ([Daemons: Introdução (parte 1)]({filename}daemons.md)).

Daemons de única instância
--------------------------

A imensa maioria dos daemons são projetados partindo do pressuposto que apenas uma instância deles estará rodando por vez. Vamos dar alguns exemplos:

- O [Nginx](https://en.wikipedia.org/wiki/Nginx) é um servidor web que escuta (_listen_) em uma determinada porta TCP (geralmente, na porta 80). Se outra instância do Nginx tentar rodar e escutar na mesma porta, ocorrerá um erro no acesso a este recurso (o sistema operacional apenas permite que um processo escute em uma porta por vez);
- O [Cron](https://en.wikipedia.org/wiki/Cron) é um daemon que roda tarefas periódicas em tempos agendados (de forma semelhante ao _Task Scheduler_ do Windows). Se várias instâncias do cron rodarem ao mesmo tempo, uma mesma tarefa, agendada para um determinado momento, iria ser executada mais de uma vez;
- O [MySQL](https://en.wikipedia.org/wiki/MySQL) é um banco de dados que estruturas de dados bastante eficientes para consultas e alterações de dados. Essas estruturas de dados, por sua vez, são persistidas em disco. Quando o usuário faz uma consulta no MySQL, esta aplicação consulta os seus arquivos ou um cache em memória pode dar a resposta da consulta. Se várias instâncias do MySQL rodarem ao mesmo tempo no sistema (mesmo que em portas diferentes) e usarem os mesmos arquivos de dados em disco, uma instância pode dar uma resposta errada ao usuário tanto porque ela respondeu a consulta confiando em seu cache local (pois os arquivos de dados foram alterados pela outra instância) quanto porque os dados em disco foram corrompidos de forma catastrófica (quando várias instâncias tentaram alterar os arquivos de dados ao mesmo tempo).

Vamos chamar esses daemons de **daemons de única instância**.

Na verdade, existem algumas variações mais complexas dos exemplos acima. Por exemplo, é possível que um administrador de sistemas utilize duas versões do Nginx, configurando cada um deles para servir um site diferente em uma porta diferente, evitando assim conflitos no uso de recursos. Vamos aqui supor que o primeiro daemon use a porta 80, e o segundo a porta 8080.

Em teoria, no exemplo acima, temos duas instâncias do mesmo daemon rodando, o que parece contrariar o fato que só podemos ter uma única instância rodando. Entretanto, se olharmos por outro ponto de vista, por usar recursos diferentes e funcionar de forma independente, podemos encarar cada um dos Nginx como sendo um daemon diferente (o primeiro daemon Nginx, da porta 80, e o segundo daemon Nginx, da porta 8080).

Essa forma de enxergar as coisas faz mais sentido ainda quando pensamos nos seguintes aspectos:

- Se um dos daemons do Nginx parar de rodar (digamos o segundo Nginx, da porta 8080), ninguém vai dizer que temos meio Nginx rodando, ou que o Nginx está rodando com metade da capacidade: de fato, todos os sites que estavam funcionando na porta 8080 param de funcionar, independente se o primeiro Nginx ainda está funcionando ou não;
- O administrador do sistema vai querer controlar cada um dos Nginx de forma independente, como se fossem serviços separados: em um momento ele poderá reiniciar o primeiro dos Nginx e, em outro momento, poderá decidir por alterar a configuração e recarregar o segundo Nginx.

O que queremos dizer é que, mesmo no caso onde existem duas instâncias do mesmo daemon, elas proverão serviços diferentes e independentes. Podemos considerar, neste caso, que temos dois daemons separados, que prestam serviços diferentes, cada um deles com a restrição de que no máximo uma única instância estará rodando.

### Pidfiles

É exatamente para evitar problemas como os descritos acima que foram desenvolvidas várias técnicas para garantir que apenas uma única instância de um daemon rode por vez. Uma técnica muito comum em ambientes Unix é o uso de um **pidfile**.

Entretanto, o conceito de pidfile é muitas vezes confundido com o conceito de _lockfile_, que por sua vez baseia-se no conceito de _lock_. Vamos então dar uma olhadinha neles:

- **Lock:** Um [lock](https://en.wikipedia.org/wiki/Lock_(computer_science)) é uma forma de garantir acesso único (exclusivo) a algum recurso, que pode ser um arquivo, uma região de código-fonte de programa, uma região da memória compartilhada, uma tabela de um banco de dados, etc;
	- O lock é uma [operação atômica](https://en.wikipedia.org/wiki/Linearizability). Assim, não corre o risco de dois processos adquirirem um lock no mesmo recurso ao mesmo tempo;
	- Por exemplo, a aplicação [Microsoft Office Excel](https://products.office.com/en/excel) adquire um lock em um arquivo de planilha (extensão `.xlsx`) quando um usuário a abre, evitando assim que outro usuário também abra a mesma planilha em modo de edição e acabe corrompendo dados;
- **Lockfile**: Em alguns casos, queremos acesso exclusivo a uma série de recursos ao mesmo tempo. Em caso como estes, o lock tradicional não é aplicável (conseguimos aplicar um lock a um recurso de forma atômica por vez, nas não conseguimos aplicar vários locks a vários recursos de forma atômica de uma única vez). Neste caso, a ideia é usar um arquivo específico, chamado de [lockfile](https://en.wikipedia.org/wiki/File_locking#Lock_files), para indicar a outro processos que você deseja utilizar de forma exclusiva toda a série de recursos em questão;
	- Por exemplo, o cliente de email [Mozilla Thunderbird](https://www.mozilla.org/en-US/thunderbird/) usa o [conceito de _profile_](http://kb.mozillazine.org/Profile_folder) (ou perfil) que, basicamente, é um diretório que contém as configurações e os emails de um usuário. Podemos ter duas instâncias do Thunderbird abertos no sistema, contanto que elas usem perfis diferentes, uma vez que duas instâncias mexendo ao mesmo tempo no mesmo perfil poderia levar a corrupção dos dados. Para garantir acesso único, ao começar a usar um perfil, o Thunderbird [cria um lockfile chamado de `parent.lock` ou `.parentlock`](http://kb.mozillazine.org/Profile_in_use#Remove_the_profile_lock_file);
	- Perceba que, se criássemos locks individuais em todos os arquivos de um perfil, problemas poderiam ocorrer. Uma instância poderia obter alguns locks em alguns arquivos, ao mesmo tempo que outra instância obteria outros locks em outros arquivos, e nenhuma delas conseguiria obter todos os locks necessários para iniciar (ambas ficaria aguardando para obter os locks restantes). Essa é uma situação clássica de [deadlock](https://en.wikipedia.org/wiki/Deadlock). O lockfile, neste caso, é uma solução simples e que evita esta problema;
	- Existem duas formas de se usar um lockfile para obter acesso exclusivo a vários recursos: a primeira é criar o lockfile de forma atômica (a existência do arquivo por si só indica que algum processo está usando os recursos), e a segunda é criar um lock no lockfile (a existência do lock no arquivo é que indica que alguém está usando os recursos). Embora a primeira forma seja mais simples, a segunda costuma ser mais compatível com diversos tipos de plataformas;
	- Tecnicamente, ao contrário de um lock tradicional, o uso de um lockfile, por si só, não proibe outros programas de acessarem os recursos ao mesmo tempo. O lockfile é um exemplo claro de programação orientada a convenções e boas práticas (ele só funciona se todas as aplicações respeitarem a convenção de não usar os recursos caso exista um lockfile);
	- Em ambientes Linux, o diretório `/var/lock` (ou `/lock`, em algumas distribuições) é frequentemente usado pelas aplicações para o armazenamento de lockfiles. Além disso, os arquivos de lockfile costumam ter a extensão `.lock`.

Agora vai ficar fácil explicar o que é um pidfile:

- **Pidfile:** Um pidfile é um lockfile usado para indicar que uma instância está rodando e que contém, em seu conteúdo, o PID da instância que está rodando;
    - Podemos pensar no pidfile como um lockfile onde o recurso em questão que queremos acesso exclusivo é a própria instância do daemon;
    - Além de garantir que apenas uma única instância está rodando, o pidfile é usado para auxiliar no controle de uma instância, uma vez que ele contém o PID da instância que está sendo executada;
    	- Conforme já explicado no artigo [Enviando e tratando sinais em processos Linux]({filename}processos-sinais.md), um método consagrado para controlar um processo é através do envio de sinais (por exemplo, através do comando `kill`) para o PID deste processo;
    - Em ambientes Linux, o diretório `/var/run` (ou `/run`, em algumas distribuições) é frequentemente usado pelas aplicações para armazenar os pidfiles. Além disso, estes arquivos costumam ter a extensão `.pid`.

#### Exemplo: O Nginx e o uso de pidfiles

Nós já falamos sobre o [Nginx](https://nginx.org/en/) anteriormente, e já mostramos [vários exemplos de como ele funciona como daemon](/daemons/#exemplo-de-funcionamento-geral-de-um-daemon) no nosso artigo anterior. Vamos, agora, usá-lo para demonstar vários dos conceitos apresentados neste artigo. Nos nossos exemplos, vamos usar um servidor Ubuntu Server 14.04 LTS.

Para instalar o Nginx:

```console
$ apt-get install nginx
```

Após o Nginx iniciar, podemos verificar que apenas uma instância de seu processo _master_ existe:

```console
$ ps aux | grep "nginx: master" | grep -v grep
root      7767  0.0  0.1  85884  1340 ?        Ss   Jul20   0:00 nginx: master process /usr/sbin/nginx
```

**Obs:** O Nginx irá criar processos filhos da instância principal, conforme já explicado em artigos anteriores. Aqui, entretanto, estamos preocupados apenas com o processo principal, chamado de master.

Ao rodar, o Nginx cria um pidfile em `/run/nginx.pid` com o seu PID (**7767**, conforme _output_ do comando `ps` anterior):

```console
$ cat /run/nginx.pid
7767
```

O nome e localização do pidfile usado pelo Nginx é configurável. Podemos encontrá-lo no arquivo principal de configuração do Nginx, em `/etc/nginx/nginx.conf`, logo no comecinho do arquivo:

```plaintext
pid /run/nginx.pid;
```

Como este arquivo contém o PID da instância nossa que está executando, podemos usá-lo como base para controlar o nosso Nginx através do envio de sinais:

```console
$ kill -s SIGHUP $(cat /run/nginx.pid)
```

Se tentarmos criar uma nova instância do Nginx através do comando `service`, veremos que nenhuma nova instância será criada:

```console
$ service nginx start
$ ps aux | grep "nginx: master" | grep -v grep
root      7767  0.0  0.1  85884  1340 ?        Ss   Jul20   0:00 nginx: master process /usr/sbin/nginx
```

Isso ocorre porque o nosso comando `service` (na realidade, o script `/etc/init.d/nginx`, usado pelo comando `service`) verifica a existência do arquivo de pidfile para decidir se iniciar ou não uma nova instância do Nginx.

Vamos agora deixar as coisas um pouquinho mais complicadas... Lembra-se do exemplo que demos de duas instâncias independentes do Nginx rodando, cada uma servindo um site diferente e em uma porta diferente? Vamos agora modificar a nossa instalação do Nginx para implementar isso.

Uma maneira de implementar este caso é usarmos dois conjuntos de arquivos de configuração diferentes (um para cada tipo de daemon), além de dois scripts de inicialização diferentes. Cada script de inicialização irá utilizar o mesmo binário (`/usr/sbin/nginx`), mas usando configurações diferentes, com portas diferentes e pidfiles diferentes. Serão dois serviços independentes.

Para fazermos isso, vamos inicialmente duplicar os arquivos de inicialização e configuração do Nginx. As cópias geradas serão usadas como base para os arquivos usados pelo novo serviço:

```console
$ cp /etc/init.d/nginx /etc/init.d/nginx2
$ cp /etc/default/nginx /etc/default/nginx2
$ cp -r /etc/nginx /etc/nginx2
```

Vamos também criar os diretórios necessários para os arquivos de log do novo serviço:

```console
$ mkdir /var/log/nginx2
$ chown --reference /var/log/nginx /var/log/nginx2
$ chmod --reference /var/log/nginx /var/log/nginx2
```

Vamos, agora, realizar as modificações necessárias nos novos arquivos criados.

No arquivo `/etc/init.d/nginx2`, fizemos as seguintes modificações:

```diff
@@ -2,5 +2,5 @@

 ### BEGIN INIT INFO
-# Provides:	  nginx
+# Provides:	  nginx2
 # Required-Start:    $local_fs $remote_fs $network $syslog $named
 # Required-Stop:     $local_fs $remote_fs $network $syslog $named
@@ -13,10 +13,11 @@
 PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
 DAEMON=/usr/sbin/nginx
-NAME=nginx
+NAME=nginx2
 DESC=nginx
+DAEMON_OPTS="-c /etc/nginx2/nginx.conf"

 # Include nginx defaults if available
-if [ -r /etc/default/nginx ]; then
-	. /etc/default/nginx
+if [ -r /etc/default/nginx2 ]; then
+	. /etc/default/nginx2
 fi
 
@@ -27,8 +28,8 @@

 # Try to extract nginx pidfile
-PID=$(cat /etc/nginx/nginx.conf | grep -Ev '^\s*#' | awk 'BEGIN { RS="[;{}]" } { if ($1 == "pid") print $2 }' | head -n1)
+PID=$(cat /etc/nginx2/nginx.conf | grep -Ev '^\s*#' | awk 'BEGIN { RS="[;{}]" } { if ($1 == "pid") print $2 }' | head -n1)
 if [ -z "$PID" ]
 then
-	PID=/run/nginx.pid
+	PID=/run/nginx2.pid
 fi
 
```

E no arquivo `/etc/nginx2/nginx.conf`:

```diff
@@ -1,5 +1,5 @@
 user www-data;
 worker_processes 4;
-pid /run/nginx.pid;
+pid /run/nginx2.pid;

 events {
@@ -24,5 +24,5 @@
 	# server_name_in_redirect off;

-	include /etc/nginx/mime.types;
+	include /etc/nginx2/mime.types;
 	default_type application/octet-stream;

@@ -31,6 +31,6 @@
 	##

-	access_log /var/log/nginx/access.log;
-	error_log /var/log/nginx/error.log;
+	access_log /var/log/nginx2/access.log;
+	error_log /var/log/nginx2/error.log;

 	##
@@ -69,6 +69,6 @@
 	##

-	include /etc/nginx/conf.d/*.conf;
-	include /etc/nginx/sites-enabled/*;
+	include /etc/nginx2/conf.d/*.conf;
+	include /etc/nginx2/sites-enabled/*;
 }

```

E no arquivo `/etc/nginx2/sites-available/default`, que define o _virtualhost_ padrão do Nginx:

```diff
@@ -19,6 +19,6 @@

 server {
-	listen 80 default_server;
-	listen [::]:80 default_server ipv6only=on;
+	listen 8080 default_server;
+	listen [::]:8080 default_server ipv6only=on;

 	root /usr/share/nginx/html;
```

Por fim, vamos corrigir o link simbólico em `/etc/nginx2/sites-enabled/default`:

```console
$ rm /etc/nginx2/sites-enabled/default
$ ln -s /etc/nginx2/sites-available/default /etc/nginx2/sites-enabled/default
```

Vamos, agora, iniciar o nosso novo serviço, o daemon que chamamos de nginx2:

```console
$ service nginx2 start
```

Observe que agora temos duas instâncias do Nginx rodando de forma independente, cada uma servindo em uma porta diferente:

```console
$ ps aux | grep "nginx: master" | grep -v grep
root     12367  0.0  0.1  85884  1336 ?        Ss   18:45   0:00 nginx: master process /usr/sbin/nginx
root     12771  0.0  0.1  85884  1340 ?        Ss   19:13   0:00 nginx: master process /usr/sbin/nginx -c /etc/nginx2/nginx.conf
$ cat /run/nginx.pid
12367
$ cat /run/nginx2.pid
12771
$ curl -s localhost | grep "<h1>"
<h1>Welcome to nginx!</h1>
$ curl -s localhost:8080 | grep "<h1>"
<h1>Welcome to nginx!</h1>
```

Criando pidfiles
----------------

No artigo anterior, [Daemons: Introdução (parte 1)]({filename}daemons.md), implementamos uma função em C chamada `deamonise` que podia ser usada para criar um daemon. Na ocasião, salvamos esta função no arquivo `daemon.c` e colocamos o seu protótipo em `daemon.h`. Depois, a utilizamos para implementar o nosso daemon `gb_daemon`, cujo código fonte foi criado no arquivo `gb_daemon.c`. Os códigos criados podem ser obtidos [na sessão "Criando um daemon"](/daemons/#criando-um-daemon) deste artigo.

Vamos, agora, fazer uma melhoria no nosso daemon, fazendo com que ele crie um pidfile durante a sua fase de inicialização para garantir que apenas uma única instância sua rode no sistema.

Para isso, no mesmo diretório que tínhamos os arquivos fontes do nosso daemon original, vamos criar um novo arquivo `daemon_pid.c` com o seguinte conteúdo:

```
#!c
#include <errno.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdio.h>

// create a pidfile
// return a negative value if the file already exists
int create_pidfile(char *pidfile) {
    int fd = 0;
    FILE *f = NULL;

    // atomically create the pidfile
    fd = open(pidfile, O_WRONLY | O_CREAT | O_EXCL, 0644);
    if (fd < 0) {
        if (errno == EEXIST) {
            return -1; // file already exists
        } else {
            exit(1); // error
        }
    }
    // associate a stream with the existing file descriptor
    f = fdopen(fd, "w");
    if (!f) {
        exit(1); // error
    }
    // write the PID in the pidfile
    fprintf(f, "%ld\n", (long)(getpid()));
    fclose(f);

    return 0;
}

// remove the pidfile
void remove_pidfile(char *pidfile) {
    unlink(pidfile);
}
```

Vamos também criar os protótipos destas funções em `daemon_pid.h`:

```
#!c
#ifndef DAEMON_PID_H
#define DAEMON_PID_H
int create_pidfile(char *pidfile);
void remove_pidfile(char *pidfile);
#endif
```

A função `create_pidfile` é responsável por criar, de forma atômica, um arquivo pidfile. Ela funciona da seguinte maneira:

- Usamos a [função `open`](https://www.gnu.org/software/libc/manual/html_node/Opening-and-Closing-Files.html) para criar um novo arquivo;
    - Passamos as [flags `O_CREAT` e `O_EXCL`](https://www.gnu.org/software/libc/manual/html_node/Open_002dtime-Flags.html#Open_002dtime-Flags) para esta função, indicando que desejamos a criação de um novo arquivo de forma exclusiva (e atômica), fazendo com que a função `open` retorne erro caso não consiga criar um novo arquivo;
    - Lembra que explicamos que existem duas formas de se usar um pidfile para indicar o uso exclusivo de recursos (usando apenas a existência do pidfile, ou usando a presença de um lock)? No nosso caso, estamos usando a primeira forma;
- Caso o arquivo pidfile já exista, retornamos o valor -1;
    - Assim, o usuário da função será informado do erro e poderá tratá-lo como quiser;
    - Quando o arquivo pidfile já existe, nenhum [_file descriptor_](https://en.wikipedia.org/wiki/File_descriptor) é retornado por `open` e a variável `errno` recebe o valor `EEXIST`;
- Usamos a [função `fdopen`](http://pubs.opengroup.org/onlinepubs/009695399/functions/fdopen.html) para associar um _stream_ (representado pela estrutura `FILE`) ao file descriptor retornado anteriormente;
    - Fizemos isso pois usar um stream deixará as coisas mais simples;
    - De forma geral, costuma-se utilizar streams (`fopen` ou `fdopen`) no lugar de usar diretamente file descriptors sempre que possível, já que isso deixa o código mais simples e, geralmente, mais eficiente. Por exemplo, a função `fwrite` usa um _buffer_ para aumentar a performance, e a função `fprintf` permite a escrita em arquivo de forma bastante simples;
- Escrevemos o PID do processo atual (obtido através da [função `getpid`](http://man7.org/linux/man-pages/man2/getpid.2.html)) no arquivo pidfile usando a [função `fprintf`](http://pubs.opengroup.org/onlinepubs/009695399/functions/fprintf.html), fechando o nosso stream na sequência;
    - Como observação, ao usar `fclose` para fechar o nosso stream `f`, o file descriptor `fd` também será fechado: `fclose` irá rodar `close(fd)` por baixo dos panos. Por este motivo, não é necessário chamarmos manualmente a função `close`.

A função `remove_pidfile`, por sua vez, é bem simples e apaga o pidfile usando a [função `unlink`](http://pubs.opengroup.org/onlinepubs/009695399/functions/unlink.html).

**Obs:** Para razões de simplicidade, implementamos o tratamento de erros da forma mais simples possível (quase sempre, apenas finalizamos o programa com _exit code_ **1**). A excessão é que informamos o usuário no caso de um arquivo pidfile já existir (linha 16). Nossa implementação resolve bem a maioria dos casos. Entretanto, recomendamos maior atenção ao tratamento de erros em uma implementação real.

**Obs:** Você também pode dar uma olhada no artigo [Advanced Programming in the UNIX Environment - Single-Instance daemon](http://poincare.matf.bg.ac.rs/~ivana/courses/tos/sistemi_knjige/pomocno/apue/APUE/0201433079/ch13lev1sec5.html), onde nós nos baseamos para criar este código-fonte. Outros exemplos também podem ser encontrados em [Stack Overflow - How to create a single instance application in C or C++](http://stackoverflow.com/questions/5339200/how-to-create-a-single-instance-application-in-c-or-c).

Vamos, agora, modificar o nosso programa `gb_daemon.c` para que ele crie um pidfile durante sua fase de inicialização. O código fonte da nova versão do nosso daemon ficará assim:

```
#!c
#include <signal.h>
#include <stdlib.h>
#include <syslog.h>
#include "daemon.h"
#include "daemon_pid.h"

#define PIDFILE "/run/gb_daemon.pid"
#define SLEEP_TIME 10

static void end_handler(int signal) {
    remove_pidfile(PIDFILE);
    syslog(LOG_NOTICE, "Program stopped");
    exit(0);
}

int main(int argc, char *argv[]) {
    // turn itself in a daemon and create the pidfile
    daemonize();
    if (create_pidfile(PIDFILE) < 0) {
        syslog(LOG_CRIT, "Pidfile %s already exists", PIDFILE);
        exit(1);
    }
    syslog(LOG_NOTICE, "Program started");
    // set end handler
    if (signal(SIGTERM, end_handler) == SIG_ERR) {
        exit(1); // error
    }
    // main loop
    while (1) {
        syslog(LOG_INFO, "Going to sleep %d seconds...", SLEEP_TIME);
        sleep(SLEEP_TIME);
        syslog(LOG_INFO, "Woke up!");
    }

    return 0;
}
```

Em relação a versão anterior, foram realizadas duas melhorias:

- Durante a fase de inicialização do daemon, a função `create_pidfile` é chamada;
    - Caso um pidfile já exista, uma mensagem de erro é logada no syslog e o programa é encerrado;
- A função `end_handler` é registrada para tratar o sinal `SIGTERM`, terminando o programa de forma "segura" (_graceful shutdown_);
    - Esta função remove o pidfile, loga no sistema que o programa encerrou, e encerra a execução do programa;
    - Mais informações sobre o sinal `SIGTERM`, sobre a função `signal` e outros conceitos sobre tratamento de sinais no Linux podem ser encontrados no nosso artigo [Enviando e tratando sinais em processos Linux]({filename}processos-sinais.md).

Estamos doidos testar o nosso daemon. Mas antes, para podermos acompanhar seus logs, vamos abrir um novo terminal e ler continuamente o syslog:

```console
$ tail -f /var/log/syslog
```

De volta ao primeiro terminal, vamos compilar a nossa nova versão e executá-la:

```console
$ gcc -o gb_daemon daemon.c daemon_pid.c gb_daemon.c
$ ./gb_daemon
```

Vamos agora verificar que o nosso daemon foi executado, e que o seu pidfile foi criado:

```console
$ ps aux | grep gb_daemon | grep -v grep
root     15702  0.0  0.0   4320   432 ?        S    01:48   0:00 ./gb_daemon
$ cat /run/gb_daemon.pid
15702
```

Podemos verificar que algumas linhas começaram a ser logadas:

```console
Jul 24 01:48:50 ubuntu-pc gb_daemon: Program started
Jul 24 01:48:50 ubuntu-pc gb_daemon: Going to sleep 10 seconds...
Jul 24 01:49:00 ubuntu-pc gb_daemon: Woke up!
Jul 24 01:49:00 ubuntu-pc gb_daemon: Going to sleep 10 seconds...
Jul 24 01:49:10 ubuntu-pc gb_daemon: Woke up!
```

Vamos tentar criar uma nova instância do nosso daemon e verificar o que acontece então:

```console
$ ./gb_daemon
$ ps aux | grep gb_daemon | grep -v grep
root     15702  0.0  0.0   4320   432 ?        S    01:48   0:00 ./gb_daemon
```

Perceba que somente o primeiro daemon está rodando no sistema. Olhando o nosso log, vemos uma entrada criada pela nossa segunda instância (às 1h58m44s), informando que o arquivo de pidfile já existia:

```console
Jul 24 01:58:40 ubuntu-pc gb_daemon: Going to sleep 10 seconds...
Jul 24 01:58:44 ubuntu-pc gb_daemon: Pidfile /run/gb_daemon.pid already exists
Jul 24 01:58:50 ubuntu-pc gb_daemon: Woke up!
```

E se enviarmos o sinal `SIGTERM` para o nosso daemon, o que ocorre?

```console
$ kill $(cat /run/gb_daemon.pid)
$ ps aux | grep gb_daemon | grep -v grep
$ cat /run/gb_daemon.pid
cat: /run/gb_daemon.pid: No such file or directory
```

Olhando os logs:

```console
Jul 24 02:04:20 ubuntu-pc gb_daemon: Going to sleep 10 seconds...
Jul 24 02:04:23 ubuntu-pc gb_daemon: Program stopped
```

Ou seja, o nosso daemon foi finalizado, removendo o seu pidfile.

Referências
-----------

- [Advanced Programming in the UNIX Environment - Single-Instance daemon](http://poincare.matf.bg.ac.rs/~ivana/courses/tos/sistemi_knjige/pomocno/apue/APUE/0201433079/ch13lev1sec5.html)
- [Stack Overflow - How to create a single instance application in C or C++](http://stackoverflow.com/questions/5339200/how-to-create-a-single-instance-application-in-c-or-c)
- [The Linux Programming Interface - Code - filelock/create_pid_file.c](http://man7.org/tlpi/code/online/dist/filelock/create_pid_file.c.html)
- [Stack Exchange - Unix - What are pid and lock files for?](unix.stackexchange.com/questions/12815/what-are-pid-and-lock-files-for)