Title: Daemons: Introdução (parte 1)
Date: 2015-10-08 13:35
Tags: linux, c, processos, daemons
Slug: daemons
Category: Linux
Summary: Neste artigo, vamos explicar um pouco sobre os daemons, processos que rodam indefinidamente em background no sistema. Vamos mostrar o que eles são, como eles funcionam e como nos comunicamos com eles. Também vamos demonstrar algumas técnicas usadas em implementações de daemons.

Este post inalgura uma série de artigos sobre _daemons_, que são processos que rodam indefinidamente no sistema.

Mesmo que você não precise desenvolver daemons, entender um pouco como eles funcionam é importante pois, quase sempre, temos inúmeros daemons rodando em um sistema operacional.

Aqui, nós vamos explicar o que são daemons, como eles funcionam e como nos comunicamos com eles. Também vamos demonstrar algumas técnicas usadas em implementações de daemons.

Para entender estes artigos, é necessário conhecer previamente alguns conceitos básicos sobre processos, como por exemplo como funciona a hierarquia de processos no Linux e como enviar e tratar sinais em um programa.

Caso você queira, você pode dar uma lida antes em alguns artigos já publicados anteriormente:

- [Tipos de processos no Linux]({filename}processos-tipos.md);
- [Enviando e tratando sinais em processos Linux]({filename}processos-sinais.md).

O que é um daemon?
------------------

[**Daemons**](https://en.wikipedia.org/wiki/Daemon_%28computing%29) são programas que ficam rodam indefinidamente, sozinhos, e em _background_ no computador. Eles não ficam interagindo diretamente com o usuário.

Por exemplo, no Linux, podemos citar o [daemon SSH](https://en.wikipedia.org/wiki/Secure_Shell#Usage), que fica rodando no sistema aguardando um usuário solicitar uma sessão SSH (para logar remotamente), e o [Apache](https://en.wikipedia.org/wiki/Apache_HTTP_Server), que fica rodando sem parar aguardando requisições web.

Outro daemon super importante é o `init`, o processo de PID 1 no Linux. Ele é um deamon tão importante que é o primeiro daemon que começa a rodar em um ambiente Unix like e, se ele parar, o sistema também para.

A maioria dos daemons são iniciados na hora do boot do sistema e finalizados no momento que o sistema desliga. Entretanto, existem as excessões: eles podem ser iniciados e finalizados de acordo com a vontade do administrador do sistema (por exemplo, através do comando `service`); além disso, como todo e qualquer programa, eles estão sujeitos a bugs e podem finalizar por falhas.

Uma outra coisa importante é que, como os daemons tem que funcionar o tempo todo, o ambiente em que eles rodam não pode estar associado a um terminal. Do contrário, ao fechar o terminal, eles iriam parar de funcionar. Dizemos que eles rodam desassociados (_detached_) de terminais.

**Obs:** Uma explicação básica do que é um terminal (TTY) pode ser encontrada [nesta pergunta no Stack Overflow](http://stackoverflow.com/questions/4426280/what-do-pty-and-tty-mean).

Por motivos semelhantes, os daemons costumam ser filhos do processo `init` e, se não forem, são filhos de outros daemons. Do contrário, eles iriam ter problemas no momento em que o pai fosse finalizado. Além disso, eles tem um comportamento independente, no sentido de que seu comportamento não depende muito do seu processo pai.

**Resumindo:** Um daemon é um processo independente que roda indefinidamente em background no sistema, desassociado de terminais.

**Obs:** Aos mais curiosos, informações sobre a origem do termo daemon podem ser obtidas [aqui](https://en.wikipedia.org/wiki/Daemon_%28computing%29#Etymology).

### Funcionamento geral de um daemon

Um daemon é desenvolvido para nunca parar: ele até pode ter uma fase de inicialização e uma fase de finalização, mas entre essas fases ele permanece em um estado onde executa uma ação continuamente. Chamamos esse estado de loop principal (ou _main loop_).

Um daemon não possui um terminal interativo e, portanto, não possui `stdin`, `stdout` e `stderr`. Sendo mais exato, ele possui esses fluxos, mas ele os aponta para `/dev/null`.

Existem também às excessões: embora vários daemons apontem o `stderr` para `/dev/null`, alguns preferem redirecioná-lo para um arquivo de log. Isso pode ser feito para simplificar o processo de log ou mesmo para evitar que alguma informação de erro seja perdida. Alguns daemons vão além: quando rodando em modo de debug, eles também redirecionam o `stdout` para um log de debug.

Por rodar em background e não poder interagir com o usuário de forma convencional (interface gráfica ou console), um daemon usa mecanismos alternativos para se comunicar com o usuário. Por exemplo, ele podem ler parâmetros de arquivos de configuração, responder a pacotes que recebe via rede, informar ao administrador o que está ocorrendo escrevendo informações em logs, ou realizam ações ao receber sinais (como recarregar um arquivo de configuração ao receber um `SIGHUP` ou finalizar em segurança ao receber um `SIGTERM`).

Anteriormente, falamos que um daemon tem um comportamento independente, e que seu comportamento não depende de um processo pai. Agora, vamos explicar um pouquinho melhor o que quisemos dizer com isso.

O Linux e outros sistemas semelhantes possuem o conceito de sessão (_session_) e grupo de processos (_process group_), além dos conceitos de líder de sessão (_session leader_) e líder de um grupo de processos (_process group leader_). De forma simplificada, ser um líder de sessão e um líder de um grupo de processos permite que um processo e seus filhos rodem de forma bastante independente no sistema, podendo ter seu próprio TTY (ou não ter TTY, como é o caso dos daemons) e fazendo com que os sinais (_signals_) que chegam até eles não sofram interfências (e nem interfiram) em outros processos.

Explicações mais detalhadas sobre os conceitos acima podem ser obtidas [aqui](https://en.wikipedia.org/wiki/Process_group) e nas [referências](#referencias) ao fim deste artigo.

Assim, para prover o isolamento necessário, uma solução é fazer com que um daemon seja líder de sessão (_session leader_) (o que automaticamente também o fará ser líder de grupo de processos (_process group leader_)).

Na prática, entretanto, é até comum fazer com que um daemon não seja líder de sessão, mas fique em uma sessão sem nenhum líder (matando o líder) "mandando" nesta sessão. O objetivo é se proteger de acidentes: um líder de sessão pode adquirir um TTY a qualquer hora, enquanto outros processos não.

Um último detalhe é que, para não atrapalhar manipulações no sistema de arquivos, um daemon geralmente muda o seu _working directory_ para a raíz do sistema (`/`). Caso contrário, ele poderia impedir desnecessariamente que um diretório fosse desmontado através do comando `umount`.

**Obs:** Em alguns casos específicos, onde um daemon depende de um _mount point_ específico, faz sentido que o daemon mude o seu _working directory_ para outro lugar que não o `/`. Mas de forma geral, o diretório `/` é o utilizado.

A figura abaixo resume o funcionamento geral de um daemon:

![Arquitetura de um daemon](/images/daemons_arquitetura.png)
{: .center }

### Exemplo de funcionamento geral de um daemon

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
