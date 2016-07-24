Title: Serviços de rede e servidores
Date: 2016-02-21 13:35
Tags: linux, python, daemons, servers
Slug: servidores-e-servicos
Category: Linux
Summary: Vamos mostrar como funcionam os servidores, sistemas que rodam indefinidamente no sistema como daemons provendo serviços sob demanda para diversos usuários ou aplicações. Vamos também implementar um pequeno servidor, mostrando as técnicas mais comuns para desenvolvê-los.
Status: Draft

No artigo anterior, [Daemons: Introdução (parte 1)]({filename}daemons.md), mostramos de forma geral como funcionam os _daemons_. Agora, neste post, mostramos um tipo de _daemon_ bem comum e super importante: o servidor.

Assim como os demais _daemons_, eles também rodam indefinidamente no sistema. Entretanto, eles provêem serviços sob demanda para vários clientes.

Assim como no artigo anterior, a regra aqui será a mesma: mesmo que você não precise desenvolver um servidor, esse artigo irá ajudar a entender um pouco como eles funcionam. Afinal, no dia-a-dia, nos deparamos com um montão deles.

Nós vamos explicar o que são os servidores (o que eles têm de especial entre os daemons) e como eles funcionam. Depois, vamos implementar um pequeno servidor web.

Para entender estes artigos, um conhecimento prévio sobre processos, daemons, sockets e protocolo HTTP é necessário. Mas não é nada de outro mundo. Caso você queira, você pode dar uma lida antes em alguns artigos já publicados anteriormente:

- [Daemons: Introdução (parte 1)]({filename}daemons.md);
- [Tipos de processos no Linux]({filename}processos-tipos.md);
- [Enviando e tratando sinais em processos Linux]({filename}processos-sinais.md).

O que é um servidor?
--------------------

Um [**Servidor**](https://en.wikipedia.org/wiki/Server_(computing)) pode ser entendido em dois sentidos: um software que provê recursos para seus clientes, ou um computador no qual rodam um ou mais softwares deste tipo.

Aqui, neste artigo, estamos focando na primeira definição: um servidor é uma aplicação que roda indefinidamente no sistema provendo recursos sob demanda a seus clientes (muitas vezes, outras aplicações). Eles implementam (junto com seus clientes) uma [arquitetura cliente-servidor](https://en.wikipedia.org/wiki/Client%E2%80%93server_model).

**Obs:** Aqui, vale lembrar que nós não estamos falando sobre os computadores do tipo servidor (_server-class hardware_) (experimente digitar no Google "comprar servidor 8GB RAM 2TB HD" que você vai achá-los). Pela nossa definição, isso não é um servidor, mas sim um computador destinado ou otimizado para ser usado como servidor (e que inclusive pode ser utilizado para outros fins). Entretanto, o termo servidor é também bastante usado para se referir a este tipo de hardware físico.

Em ambientes Linux e outros ambientes _UNIX like_, os servidores geralmente são _daemons_ (no Windows, por outro lado, eles são geralmente implementados como "Windows Services", mas vamos focar aqui em ambientes Linux). Assim, os usuários não conseguem interagir diretamente com eles, visto que eles não rodam em _foreground_, mas em _background_ no sistema.

Para se comunicar com um servidor, geralmente usamos sinais, arquivos de configuração, protocolos TCP/IP, etc. Aliás, a imensa maioria dos servidores utilizam protocolos de rede (camada de aplicação da pilha TCP/IP) para se comunicar com seus clientes.

É comum também entender o servidor como sendo um programa que provê algum tipo de serviço (entregar páginas web é um serviço, nesse contexto), e que este serviço, por sua vez, consiste em permitir ao cliente ter acesso a uma série de recursos (uma página web, por exemplo, pode ser um recurso).

Para dar um exemplo, para um site simples funcionar, geralmente são necessários no mínimo 3 servidores: um servidor DNS, para resolver as URLs do site (como o [Bind](https://en.wikipedia.org/wiki/BIND)), um servidor web, para servir os arquivos estáticos e gerar as páginas dinâmicas (como o [Apache](https://en.wikipedia.org/wiki/Apache_HTTP_Server)), e um servidor de banco de dados, para permitir o armazenamento e atualização dos dados do site (como o [MySQL](https://en.wikipedia.org/wiki/MySQL)).

Como os servidores atendem seus clientes?
-----------------------------------------

Em seu ciclo de vida, um servidor inicializa, roda seu loop principal (_main loop_) por um longo período de tempo e, por fim, finaliza.

Durante a fase de inicialização, um servidor faz coisas como ler seus arquivos de configuração, carregar seus dados, abrir arquivos de log, escutar em uma ou mais portas de rede (_listen_), etc). Já durante o seu _main loop_, o servidor fica esperando ansiosamente pela chegada de clientes, atendendo-os a medida em que eles aparecem, entregando os recursos que eles requisitaram.

Uma questão então surge: como atender a vários clientes de forma eficiente, sendo que eles podem aparecer a qualquer momento e em qualquer ordem, com alguns momentos sem nenhum cliente, outros com apenas um, e outros com múltiplos deles em paralelo?

Para entender melhor este problema, vamos supor um servidor bem simples, que atende um usuário de cada vez, na ordem de sua chegada. Para isso, ele escuta (_listen_) em uma porta e aguarda a conexão de um usuário. Ao receber esta conexão, ele para o que estava fazendo (aguardar conexões) e foca em obter o recurso requisitado pelo cliente (etapa que pode demorar algum tempo, exigindo cálculos computacionais ou uma série de acessos ao disco). De posse do recurso, o servidor o envia ao cliente e então fecha a conexão. Somente depois, com o cliente já atendido, o servidor volta a aguardar por conexões de novos clientes.

Entretanto, enquanto o servidor está preparando a resposta de um cliente, é possível que um novo cliente chegue (abra uma conexão). Se isto ocorrer, este cliente irá ficar aguardando em uma fila (criada pelo Sistema Operacional). De forma semelhante, se outros usuários chegarem ao sistema, eles serão adicionados nesta mesma fila. Quando o servidor terminar de atender a requisição do primeiro usuário e voltar a verificar por novas conexões, ele vai imediatamente passar para ele o primeiro usuário que estava aguardando na fila, e esse usuário será então atendido.

Um problema desse modelo é que vários clientes podem ficar esperando bastante tempo na fila (e, desde filas do Sistema Operacional a filas de banco ou filas para comprar ingressos, ninguém gosta de ficar esperando em filas :(). Esse problema incomoda ainda mais quando o primeiro cliente pede algo demorado, enquando os demais clientes só querem recursos simples e rápidos de se obter (imagine-se tendo que esperar 30min na fila de um caixa de supermercado, esperando que um cliente termine as compras do mês, só para depois você poder comprar o seu biscoito).

Vamos fazer um exemplo prático (iremos usá-lo mais a frente para fins de comparação): suponha que, em determinado momento, cheguem 4 clientes simultaneamente, que o primeiro cliente faça um requisição que demore 8s, e que os demais façam requisições que demorem 1s. O quarto cliente, então, terá que aguardar 11s na fila para ser atendido, e o seu tempo total de resposta será de 12s. Bem ruim :(!

Para entender como podemos resolver este problema, vamos supor uma pequena modificação no nosso servidor original. Assim como antes, no início, ele fica aguardando por conexões de clientes. Ao receber a primeira conexão, ele cria um novo programa e passa a conexão para este novo programa. Este último programa, por sua vez, realiza a computação necessária e entregua o recurso ao cliente. Assim que passar a conexão para o novo programa, o servidor então volta a aguardar por novas conexões. Uma vez que o servidor não faz mais trabalhos computacionalmente demorados, ele está quase o tempo todo livre e aguardando conexões de novos clientes (ele é um recepcionista de clientes, que rapidamente os recebe e os repassa para outros programas).

Po um lado, não temos mais ninguém esperando na fila. Por outro, como temos vários recursos sendo calculados em paralelo no sistema, 

A figura abaixo resume o funcionamento geral de um daemon:

![Arquitetura de um daemon](/images/daemons_arquitetura.png)
{: .center }

### Exemplo de funcionamento geral de um daemon

Talvez poque a função do servidor é prover um ou mais serviços a seus clientes, o galera do [Debian](https://en.wikipedia.org/wiki/Debian) e de Sistemas Operacionais derivados dele costumam usar o comando serviço (`service`) para iniciar ou finalizar servidores (no fundo, iniciar ou finalizar os serviços que eles provêem).



Vamos, agora, analisar alguns aspectos do funcionamento do [Nginx](http://nginx.org/), um servidor web (que também é um daemon).

O Nginx é o servidor web usado para servir as páginas deste lindo blog que é o GBzando.

Na nossa experiência, vamos analisar uma instalação real do Nginx em um Ubuntu Server 14.04 LTS instalado via `apt-get`.

Vamos começar dando uma olhada na árvore de processos do sistema:

```console
$ pstree
init─┬─acpid
[...]
     ├─nginx───nginx
[...]
     ├─sshd───sshd───sshd───bash───sudo───su───bash───pstree
[...]
```

No output acima, vemos toda a cadeia de processos acima do processo `pstree` (comando que executamos), além de dois processos Nginx. Os demais processos foram ocultados.

Veja que o Nginx possui 2 processos: um pai e principal, que chamamos de _master_, e um filho, que chamamos de _worker_. A diferença entre os dois vai ser mostrada mais a frente nesta série de artigos. Por ora, vamos focar no processo principal (o master).

Comparando os processos `nginx` e `pstree`, de cara, vemos que o `nginx` é filho do processo `init`, o que lhe confere uma boa "independência". Já o `pstree` roda dentro de um shell `bash` (ele depende desse processo), que por sua vez possui como ancestral uma sessão SSH (`sshd`). Se a sessão SSH cair, os seus diversos descendentes serão impactados, o que não irá ocorrer com o nosso Nginx.

Vamos agora rodar o comando `ps` para obter mais informações:

```console
$ ps aux | grep -e "CPU" -e "nginx" -e "ps aux" | grep -v "grep"
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root      1031  0.0  0.4 132296  2420 ?        Ss   Sep27   0:00 nginx: master process /usr/sbin/nginx
www-data  1032  0.0  0.7 132692  3572 ?        S    Sep27   0:01 nginx: worker process
root      8315  0.0  0.2  17164  1324 pts/0    R+   15:07   0:00 ps aux
```

Usamos alguns `grep`'s para filtrar o nosso output, mostrando apenas os processos que nos interessam.

Olhando o output, vemos que:

- Os nossos processos `nginx` não possuem TTY (terminal), ao passo que o comando `ps` foi executado no terminal `pts/0`;
- O processo Nginx master possui a flag STAT `s`, que significa que ele é um líder de sessão, ao passo que o comando `ps` possui a flag `+`, que mostra que ele está rodando em foreground no sistema (o nosso Nginx, que roda em background, não possui esta flag);
- Os processos Nginx possuem a flag `S`, que mostra que eles estão em _interruptible sleep_, que geralmente significa que ele está aguardando por algum evento. Isso é um comportamento comum em daemons, que muitas vezes ficam bastante tempo no sistema parados em seu _main loop_ aguardando que algo ocorra (como a chegada de um pacote TCP na porta 80, no nosso caso específico). Já o comando `ps` possui a flag `R`, que mostra que ele está em estado _running_, comportamento comum em processos em foreground.

**Obs:** Uma explicação sobre as flags da coluna STAT do comando `ps` pode ser vista [nesta resposta do Ask Ubuntu](http://askubuntu.com/a/360253/197497).

Para facilitar a análise de mais outros conceitos, vamos deixar um comando `sleep` rodando em background no sistema para poder comparar seu comportamento com o do nosso daemon:

```console
$ cd /root
$ sleep 9999 &
[1] 8385
```

O nosso Nginx master está usando o PID 1031, e o nosso `sleep` está rodando com o PID 8385. De posse desses PIDs, podemos usar o diretório `/proc` para obter mais informações sobre os nossos programas:

```console
$ ls -lh /proc/1031/cwd
lrwxrwxrwx 1 root root 0 Oct  6 15:31 /proc/1031/cwd -> /
$ ls -lh /proc/1031/fd/[0-2]
lrwx------ 1 root root 64 Oct  6 15:47 /proc/1031/fd/0 -> /dev/null
lrwx------ 1 root root 64 Oct  6 15:47 /proc/1031/fd/1 -> /dev/null
l-wx------ 1 root root 64 Oct  6 15:47 /proc/1031/fd/2 -> /var/log/nginx/error.log
$ ls -lh /proc/8385/cwd
lrwxrwxrwx 1 root root 0 Oct  6 15:48 /proc/8385/cwd -> /root
$ ls -lh /proc/8385/fd/[0-2]
lrwx------ 1 root root 64 Oct  6 15:48 /proc/8385/fd/0 -> /dev/pts/0
lrwx------ 1 root root 64 Oct  6 15:48 /proc/8385/fd/1 -> /dev/pts/0
lrwx------ 1 root root 64 Oct  6 15:48 /proc/8385/fd/2 -> /dev/pts/0
```

**Obs:** Explicações sobre o `/proc` podem ser obtidas [neste artigo na Wikipedia](https://en.wikipedia.org/wiki/Procfs).

Analisando o output acima, podemos tirar as seguintes conclusões:

- O nosso Nginx usa o diretório raiz `/` como _working directory_ (_cwd_ é uma sigla para _current working directory_), o que concorda com o comportamento esperado de um daemon. Já o processo `sleep` usa o `/root` como _working directory_;
- O processo `sleep` possui os seus três streams padrão (`stdin`, `stdout` e `stderr`, _file descriptors_ 0, 1 e 2, respectivamente) apontados para o terminal `pts/0`. Isso é, ele usa um terminal para se comunicar com o usuário;
- O processo Nginx, entretanto, possui o `stdin` e `stdout` apontando para `/dev/null`, como é comum ocorrer com um daemon. O diferente aqui é o `stderr` apontado para um arquivo de log (`/var/log/nginx/error.log`).

Além do main loop, o Nginx possui uma fase de inicalização onde, dentre outras coisas, ele lê e interpreta seu arquivo de configuração. No nosso caso, este arquivo fica em `/etc/nginx/nginx.conf`. Ele também possui uma fase de encerramento, onde ele aguarda que todos os seus filhos terminem de servir as páginas atuais (ou seja, concluírem seu trabalho) para, somente depois, encerrar.

Para interagir com nosso daemon, além dos arquivos de log e configuração, podemos enviar pacotes TCP via rede, ou enviar sinais (_signals_).

Em relação aos sinais, o nosso Nginx recarrega o arquivo de configuração ao receber um `SIGHUP`, reabre seus arquivos de logs ao receber um `SIGUSR1`, e finaliza de forma segura (_graceful shutdown_) ao receber um `SIGQUIT`. A especificação completa é encontrada [aqui](http://nginx.org/en/docs/control.html). O arquivo `etc/init.d/nginx`, por exemplo, usa esses sinais para controlar o Nginx.

Por fim, para não deixarmos nenhum processo executando em background:

```console
$ killall sleep
[1]+  Terminated              sleep 9999
```

Criando um daemon
-----------------

Primeiramente, se você pretende criar um daemon em produção, **não** recomendamos usar diretamente o código que iremos mostrar aqui. Ele não representa a forma mais simples e eficiente de se criar um daemon em um sistema moderno, e está aqui para fins didáticos. As ferramentas mais modernas e eficientes para se criar daemons serão apresentadas em outros artigos.

Vamos relembrar alguns conceitos mostrados no artigo [Tipos de processos no Linux]({filename}processos-tipos.md):

- Quando o pai de um processo morre, o comportamento padrão do filho é ser adotado pelo processo `init`;
- Além disso, como um processo herda o terminal do processo pai, ao ser adotado pelo `init`, o processo filho irá herdar o terminal do `init` (no caso, como o `init` não tem terminal, o processo filho irá ficar sem terminal).

Iremos usar uma técnica chamada [fork off and die](http://wiki.linuxquestions.org/wiki/Fork_off_and_die) para criar nosso daemon. Em essência, essa técnica usa os conceitos apresentados acima e alguns outros novos que iremos mostrar no decorrer dessa sessão.

O algoritmo completo que iremos usar segue as ideias listadas [aqui neste artigo da Wikipedia](https://en.wikipedia.org/wiki/Daemon_%28computing%29#Creation). Ele é também baseado no algoritmo de exemplo no artigo [Linux Network Programming - daemon_init Function](http://www.masterraghu.com/subjects/np/introduction/unix_network_programming_v1.3/ch13lev1sec4.html).

Vamos, inicialmente, criar a nossa função que gera daemons no arquivo `deamon.c`:

```
#!c
#include <stdlib.h>
#include <signal.h>
#include <sys/resource.h>
#include <fcntl.h>

// transform the program into a daemon
void daemonize(void) {
    int i = 0;
    pid_t pid = 0;
    struct rlimit rlimit;

    // first fork and die (generate first child)
    pid = fork();
    if (pid >= 0) { // fork successful
        if (pid != 0) { // if parent, die
            exit(0);
        }
    } else { // error
        exit(1);
    }

    // become a session leader
    if (setsid() < 0) {
        exit(1); // error
    }

    // ignore SIGHUP
    if ((signal(SIGHUP, SIG_IGN) == SIG_ERR)) {
        exit(1); // error
    }

    // second fork and die (generate second child)
    pid = fork();
    if (pid >= 0) { // fork successful
        if (pid != 0) { // if first child, die
            exit(0);
        }
    } else { // error
        exit(1);
    }

    // set appropriate umask
    umask(0);

    // set root as working dir
    if (chdir("/") < 0) {
        exit(1); // error
    }

    // close all file descriptors
    if (getrlimit(RLIMIT_NOFILE, &rlimit) < 0) {
        exit(1); // error
    }
    for (i = 0; i < rlimit.rlim_max; i++) {
        close(i);
    }

    // redirect stdin/stdout/stderr to null
    open("/dev/null", O_RDONLY);
    open("/dev/null", O_RDWR);
    open("/dev/null", O_RDWR);
}
```

Vamos também criar o protótipo dessa função em `daemon.h`:

```
#!c
#ifndef DAEMON
#define DAEMON
void daemonize(void);
#endif
```

A nossa função faz o seguinte ao ser chamada de dentro de um processo qualquer:

- O processo realiza um `fork`, criando um filho, e depois encerra;
    - Neste momento, conforme explicado anteriormente, o filho é herdado pelo processo `init` e fica sem terminal;
    - Além disso, poderemos garantir que o filho **não** será um líder de sessão;
        - No Linux, a sessão de um processo é identificada por um número chamado SID, que é o PID do processo líder daquela sessão;
        - Além disso, ao ser criado, o filho é inserido da mesma sessão que o processo pai;
        - Como o filho é criado com um novo PID, nós garantimos que esse valor será diferente do seu SID (que será o PID do pai ou de algum outro processo acima do pai);
- Depois, usamos a função `setsid` para iniciar uma nova sessão, fazendo com que o filho se torne um líder de sessão;
- Na sequência, nós ignoramos sinais `SIGHUP`;
    - Nós fazemos isso, pois, logo depois, nós iremos realizar outro _fork off and die_ e, como o nosso processo atual é um líder de sessão, matar uma sessão propaga por padrão sinais `SIGHUP` para os filhos, e nós não queremos isso;
- Depois, nós repetimos a técnica de realizar um `fork` e morrer (essa técnica é chamada de _fork twice_);
    - Nós fazemos isso para que o novo filho não seja um líder de sessão (embora fique "mandando" em uma sessão independente). Segundo já explicamos, isso é só para evitar acidentes, já que um líder de sessão poderia solicitar um terminal à qualquer momento;
- Depois, nós reiniciamos o _umask_ usado pelo daemon;
    - Se não fizermos isso, o nosso daemon pode rodar com um valor de _umask_ indeterminado, pois não teremos controle sobre o _umask_ do usuário que iniciar o daemon no sistema;
- Depois, nós mudamos o _working directory_ para o diretório raíz;
- Depois, nós fechamos todos os file descriptors. Isso inclui o `stdin`, `stdout` e `stderr`, além de outros arquivos que o nosso programa por ventura tenha aberto antes de chamar a nossa função;
- Por fim, nós redirecionamos o `stdin`, o `stdout` e o `stderr` para `/dev/null`.

Neste momento, pedimos desculpas por tantas mortes :(. Solicitamos um minuto de silêncio em respeito aos processos mortos.

**Obs:** Em caso de dúvidas, você pode dar uma olhada no artigo [Linux Network Programming - daemon_init Function](http://www.masterraghu.com/subjects/np/introduction/unix_network_programming_v1.3/ch13lev1sec4.html), onde nós nos baseamos para criar este código-fonte. Este artigo também explica muito bem vários conceitos usados no nosso código.

Agora, vamos implementar o nosso daemon no arquivo `gb_daemon.c`:

```
#!c
#include <syslog.h>
#include "daemon.h"

#define SLEEP_TIME 10

int main(int argc, char *argv[]) {
    // turn itself in a daemon
    daemonize();
    syslog(LOG_NOTICE, "Program started");

    // main loop
    while (1) {
        syslog(LOG_INFO, "Going to sleep %d seconds...", SLEEP_TIME);
        sleep(SLEEP_TIME);
        syslog(LOG_INFO, "Woke up!");
    }
}
```

O nosso daemon é bem simples:

- Em sua fase de inicialização, ele chama a função `daemonize` para tornar-se um daemon e depois usa a função `syslog` para logar no syslog do sistema;
    - A novidade aqui é o [sistema de logs via syslog](http://www.gnu.org/software/libc/manual/html_node/Submitting-Syslog-Messages.html). Nós só estamos usando o básico do básico deste sistema: _logando_ mensagens, que irão aparecer no arquivo `/var/log/syslog`, usando a configuração padrão;
- Em seu main loop, ele dorme (`sleep`) durante um tempo fixo, _loga_ algumas mensagens, e depois torna a dormir novamente, repetindo o processo indefinidamente.

Para podermos acompanhar o nosso novo daemon, vamos antes abrir um novo terminal e ler continuamente o syslog:

```console
$ tail -f /var/log/syslog
```

Agora, no primeiro terminal, vamos compilar e rodar o nosso daemon:

```console
$ gcc -o gb_daemon daemon.c gb_daemon.c
$ ./gb_daemon
```

Depois de executar o daemon, nós iremos tomar controle novamente do terminal. Isso ocorre mais precisamente no momento em que o primeiro pai, que rodava em foreground no sistema, morre.

Agora, se você verificar o segundo terminal (que deixamos aberto com o output do `/var/log/syslog`), vai verificar mensagens como as que estão abaixo:

```console
Oct  8 10:59:33 ubuntu-server gb_daemon: Program started
Oct  8 10:59:33 ubuntu-server gb_daemon: Going to sleep 10 seconds...
Oct  8 10:59:43 ubuntu-server gb_daemon: Woke up!
Oct  8 10:59:43 ubuntu-server gb_daemon: Going to sleep 10 seconds...
Oct  8 10:59:53 ubuntu-server gb_daemon: Woke up!
Oct  8 10:59:53 ubuntu-server gb_daemon: Going to sleep 10 seconds...
```

Podemos então fechar o nosso comando `tail` (pressionando `CTRL+C`) e, depois, fechar esse nosso segundo terminal.

Voltando ao primeiro terminal, vamos repetir os mesmos testes que fizemos no nosso exemplo do Nginx para verificar que o nosso daemon está rodando conforme esperado:

```console
$ pstree
init─┬─acpid
[...]
     ├─gb_daemon
[...]
$ ps aux | grep -e "CPU" -e "gb_daemon" | grep -v "grep"
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
rarylson 10425  0.0  0.0   4320   428 ?        S    13:59   0:00 ./gb_daemon
$ ls -lh /proc/10425/cwd
lrwxrwxrwx 1 rarylson rarylson 0 Oct  8 14:33 /proc/10425/cwd -> /
$ ls -lh /proc/10425/fd/[0-2]
lr-x------ 1 rarylson rarylson 64 Oct  8 14:34 /proc/10425/fd/0 -> /dev/null
lrwx------ 1 rarylson rarylson 64 Oct  8 14:34 /proc/10425/fd/1 -> /dev/null
lrwx------ 1 rarylson rarylson 64 Oct  8 14:34 /proc/10425/fd/2 -> /dev/null
```

Por fim, vamos fechar o nosso daemon enviando um sinal `SIGTERM` (o padrão do `kill`) para ele:

```console
$ kill 10425
```

Referências
-----------

- [Wikipedia - Deamon](http://en.wikipedia.org/wiki/Daemon_%28computing%29)
- [Wikipedia - Process Group](https://en.wikipedia.org/wiki/Process_group)
- [The Linux Kernel - Processes](http://www.win.tue.nl/~aeb/linux/lk/lk-10.html)
- [Linux Network Programming - daemon_init Function](http://www.masterraghu.com/subjects/np/introduction/unix_network_programming_v1.3/ch13lev1sec4.html)
- [Advanced Programming in the UNIX Environment: Second Edition - Chapter 13. Daemon Processes](http://poincare.matf.bg.ac.rs/~ivana/courses/tos/sistemi_knjige/pomocno/apue/APUE/0201433079/ch13lev1sec3.html)

http://www.linuxhowtos.org/C_C++/socket.htm
http://man7.org/linux/man-pages/man2/bind.2.html
