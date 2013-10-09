Title: Sinais, processos zumbis e processos órfãos
Date: 2013-09-29 15:00
Tags: linux, shell, c
Slug: processos-zumbi-orfaos
Category: Linux
Author: Rarylson Freitas
Summary: Entenda melhor o que são processos órfão e zumbis. Neste artigo, mostraremos como reproduzí-los através de diversas experiências e programas em C, e você entenderá os motivos que podem levar a sua aparição em servidores.
Status: draft

Em um artigo anterior, chamado [Tipos de processos no Linux]({filename}/processos-tipos.md), mostramos como funcionam os diversos tipos de processos e como funciona a hierarquia de processos no Linux.

Agora, iremos realizar diversas experiências para mostrar como podemos simular o aparecimento de processos zumbis e processos órfãos. Além disso, iremos mostrar como evitar que eles ocorram. Processos com estas características costumam surgir, muitas vezes, devido a falhas de programação ou operação incorreta do sistema operacional.

Para isso, iremos mostrar também um pouco de sinais (_signals_) no Linux.

Sinais no Linux
---------------

Enviar sinais ([_signals_](http://en.wikipedia.org/wiki/Unix_signal)) é uma forma simples de comunicação entre processos utilizada no Linux (e outros sistemas _Unix like_). É um tipo de comunicação assíncrona e baseada em eventos.

De forma simplificada, um processo envia um sinal para outro processo e este, ao receber o sinal, terá sua linha de execução interrompida e irá executar o _handler_ daquele sinal.

Existem sinais para muitos tipos de evento. No artigo passado, foram apresentados explicitamente o SIGHUP, o SIGSTOP e o SIGTERM. Implicitamente, apresentamos o SIGTERM (semelhante ao SIGHUP, é o sinal padrão enviado pelo `kill` e pelo `killall`) e o SIGTSTP (parecido com o SIGSTOP, ocorre ao pressionar `CTRL+Z` no terminal em um processo em _foreground_).

Cada um desses sinais possui um comportamento _default_ definido pelo sistema operacional. A maioria deles [pode ser sobrescrito](http://en.wikipedia.org/wiki/C_signal_handling) (alguns poucos outros não).

Por exemplo, uma [diferença entre o SIGSTOP e o SIGTSTP](http://stackoverflow.com/a/11888074) é que o primeiro não pode ser sobrescrito pelo programa que irá receber o sinal. Entretanto, poderia ser definido um _handler_ específico para o segundo sinal responsável, por exemplo, por executar ações visando manter a consistência dos dados antes do programa ser suspendido.

Alguns outros sinais são:

- **SIGINT:** Muito semelhante ao SIGTERM, ocorre ao pressionar `CTRL+C` no terminal em um processo em _foreground_;
- **SIGKILL:** Parecido com o SIGINT e o SIGTERM, mas não pode ser sobrescrito;
- **SIGCHLD:** **Geralmente** informa a um processo pai que algum filho terminou a execução;
    - Embora possa ser [enviado em outros casos](http://en.wikipedia.org/wiki/Child_process), o caso acima é o que nos interessa neste artigo.

Sobrescrevendo sinais
---------------------

Vamos agora apresentar um programa que irá sobrescrever o comportamento padrão de um _signal haldler_. Iremos chamá-lo de **i_will_survive.c**:

    #!c
    #include <signal.h>
    #include <stdio.h>
    
    // handler for common signals that terminate process
    static void end_handler(int signal) {
        printf("I will survive, baby!\n");
    }
    
    int main(int argc, char *argv[]) {
        // set handlers
        if ((signal(SIGINT, end_handler) == SIG_ERR) || (signal(SIGHUP, end_handler) ==  
                SIG_ERR) || (signal(SIGTERM, end_handler) == SIG_ERR)) {
            printf("Error while setting a signal handler\n");
            return 1;
        }   
        while (1) { } // infinite loop
        return 0;  
    }

Este programa define a [função estática](http://codingfreak.blogspot.com/2010/06/static-functions-in-c.html) `end_handler` como o handler dos sinais SIGINT, SIGHUP e SIGTERM através da função [signal](http://www.cplusplus.com/reference/csignal/signal/). Logo após, ele entra em um loop infinito. 

Vamos executá-lo em _foreground_ e, logo após, pressionar `CTRL+C` algumas vezes para enviar sinais SIGINT:

    :::bash
    gcc -o i_will_survive i_will_survive.c
    ./i_will_survive
    > ^CI will survive, baby!
    > ^CI will survive, baby!

Ao receber o sinal, a função `end_handler` é executada e é impresso "I will survive" na tela.

Vamos agora abrir um outro terminal e obter o PID do processo:

    :::bash
    ps aux | grep i_will_survive | grep -v grep
    > rarylson       55300  98.5  0.0  2432744    480 s003  R+   11:39PM   0:10.66 ./i_will_survive

Agora, iremos enviar vários sinais usando o comando `kill`:

    :::bash
    kill 55300
    kill -s SIGHUP 55300
    kill -s SIGINT 55300

O primeiro comando enviará um SIGTERM (o sinal padrão do `kill`). 

No primeiro terminal, vemos que o processo continua executando:

    :::bash
    > I will survive, baby!
    > I will survive, baby!
    > I will survive, baby!

Vamos agora no segundo terminal e enviar um sinal SIGKILL:

    :::bash
    kill -s SIGKILL 55300

Convém observar que SIGKILL é o sinal de número 9. Assim, o comando `kill -9 55300`, comum nos fóruns sobre Linux, faz exatamente a mesma coisa que o comando acima.

Desta vez, no primeiro terminal, verificamos que o processo finalmente morreu:

    :::bash
    > Killed: 9

Agora, vamos supor que um certo programados quer sobrescrever o _handler_ de SIGKILL. O que irá ocorrer?

Neste caso, vamos modificar a **linha 12** do programa **i_will_survive.c** para:

    :::c
    // SIG_ERR) || (signal(SIGTERM, end_handler) == SIG_ERR)) {
    SIG_ERR) || (signal(SIGTERM, end_handler) == SIG_ERR) ||
    (signal(SIGKILL, end_handler) == SIG_ERR)) {
    
Recompilando e executando o programa:

    :::bash
    gcc -o i_will_survive i_will_survive.c
    ./i_will_survive
    > Error while setting a signal handler

Ou seja, de fato, não é possível sobrescrever o _handler_ default de SIGKILL.

Usando processos órfãos para criar um deamon
--------------------------------------------

Um [**deamon**](http://en.wikipedia.org/wiki/Daemon_%28computing%29) é um processo independente que roda em _background_ no sistema. Ser independente significa que seu comportamento não depende do seu processo pai.


No artigo [Tipos de processos no Linux]({filename}/processos-tipos.md), mostramos que:

- O filho de um processo herda o terminal tty do pai;
    - Uma explicação básica do que é tty pode ser encontrada [aqui](http://stackoverflow.com/questions/4426280/what-do-pty-and-tty-mean);
- Quando o pai de um processo morre, o comportamento padrão é que o filho seja adotado pelo processo **init**.

Usaremos isso como base para criar um processo _deamon_. Iremos gerar um processo que, no fim, seja filho de **init** e não possua terminal.

O processo adotado será uma simplificação do processo correto (chamado de [fork off and die](http://wiki.linuxquestions.org/wiki/Fork_off_and_die)) pois não iremos nos preocupar (a exceção do tty) com uma série de características que o _deamon_ herdará do seu pai original (**stdin**, **stdout**, **umask**, dentre outras).

Para isso, vamos criar um arquivo com o nome **deamon.c**:



No exemplo acima, o processo inicial irá criar um filho que, por sua vez, irá chamar a função `setsid` para iniciar uma nova sessão. Após esse processo inicial, o filho será o líder de sessão (_session leader_) de seu grupo de processo.

Para entender melhor o que isto significa, você poderá ler a [Seção 10.3 de The Linux Kernel - Process](http://www.win.tue.nl/~aeb/linux/lk/lk-10.html) e [esta pergunta no Stack Overflow](http://stackoverflow.com/questions/2613104/why-fork-before-setsid). Neste artigo, estmaos apenas interessado em 


Referências
-----------

- [Wikipedia - Unix signal](http://en.wikipedia.org/wiki/Unix_signal)
- [Linux Man - Signal](http://man7.org/linux/man-pages/man7/signal.7.html)
- [Signals (and Zombie and SIGCHLD)](http://www.win.tue.nl/~aeb/linux/lk/lk-5.html)
- [Wikipedia - Zombie Process](http://en.wikipedia.org/wiki/Zombie_process)
- [The Linux Kernel - Process](http://www.win.tue.nl/~aeb/linux/lk/lk-10.html)
- [Wikipedia - Deamon](http://en.wikipedia.org/wiki/Daemon_%28computing%29)
