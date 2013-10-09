Title: Tipos de processos no Linux
Date: 2013-09-28 10:00
Tags: linux, shell, c
Slug: processos-tipos
Category: Linux
Author: Rarylson Freitas
Summary: Entenda o que é um processo em sleep, wait, zombie, órfão, e como funciona a árvore de processos do Linux. Neste artigo, mostramos o que eles são, e como reproduzí-los através do uso de comandos Linux e programação em C.

No Linux (e em outros sistemas baseados em Unix, chamados _Unix like_), um processo pode ter diversos estados (ativo, em espera, dormindo, etc), e existe uma hierarquia entre os processos (árvore de processos).

Vamos fazer algumas experiências buscando entender como funcionam os diferentes tipos de processos.

Estados de um processo
----------------------

Em sistemas Linux, os processos possuem um dos seguintes estados:

- **Running:** Processo ativo, rodando normalmente no sistema;
    - É importante ver que este processo pode não estar rodando, naquele instante, no processador. Ele pode apenas estar na fila de processos prontos (_ready queue_), podendo ser escalonado a qualquer momento;
- **Sleeping:** Também chamado de **interruptible sleep**, é um processo dormindo por um tempo finito. Este processo fica em uma fila diferente, não consome CPU, e voltará para a _ready queue_ quando o seu tempo de _sleep_ acabar;
- **Waiting:** Também chamado de **uninterruptible sleep**, é um processo esperando por algum evento ou por algum recurso do sistema;
    - Existe uma diferença conceitual entre processos _sleeping_ e _waiting_: o momento que eles voltam à execução. O processo em _sleeping_ volta após algum tempo bem definido, ao passo que o processo em _waiting_ volta após um tempo indefinido, quando ocorrer algum evento que coloque-o novamente na _ready queue_;
    - Este estado é comum em casos de sincronismo (espera por lock) ou quando um processo está esperando para acessar o disco (espera por I/O);
    - Uma falha de implementação pode permitir que um processo entre em estado _waiting_ e nunca saia deste estado. Neste caso, temos um [deadlock](http://www.makelinux.net/books/lkd2/ch08lev1sec3);
- **Suspended:** Também chamado de **stopped**, este estado é geralmente obtido quando o usuário dá um _stop_ em um processo. Quando o usuário executa um _resume_, o processo retorna a _ready queue_ e voltará a executar do exato ponto (instrução) em que havia parado;
- **Zombie:** Também chamado de **defunct**, é um processo que finalizou a execução (e portanto não ocupa memória), mas que ainda possui uma entrada na tabela de processos, porque seu processo pai ainda não "tomou conhecimento" que o filho terminou;
    - No fluxo normal, o pai, ao ser notificado que o filho terminou, desaloca recursos desnecessários e executa outras ações necessárias, e depois o sistema retira o processo filho da tabela de processos;
    - Se o pai não realizar nenhuma ação, o filho permanecerá na tabela de processos (como um processo zumbi) até que o pai termine sua execução.

Árvore de processos
-------------------

No Linux, cada processo possui um pai (o processo que o criou). A exceção é o processo **init**, que é o processo raiz da árvore de processos do sistema operacional.

Para ver a árvore de processos, podemos utilizar o comando `pstree`. Um exemplo de output seria:

    :::bash
    pstree -a
    > init
    >   ├─accounts-daemon
    >   │   └─{accounts-daemon}
    >   ├─apache2 -k start
    >   │   ├─apache2 -k start
    >   │   ├─apache2 -k start
    >   │   ├─apache2 -k start
    >   │   ├─apache2 -k start
    >   │   └─apache2 -k start
    >   ├─atd
    >   ├─automount
    >   │   └─2*[{automount}]
    >   ├─cron
    >   │   └─cron
    >   │       └─bash /usr/local/bin/gbzando/test.sh

O argumento `-a` fará com que os argumentos passados na hora da execução dos processos (como o `-k start`) sejam mostrados. O `pstree` possui outros argumentos interessantes, como o `-p`, usado para imprimir os PIDs.

Na saída acima, vemos que:

- O processo **init** é o pai de todos os demais;
- Existe um processo **Apache** principal com 5 filhos (_deamon_ usando o [prefork](http://httpd.apache.org/docs/2.2/mod/prefork.html));
- Existe um script `test.sh` que foi disparado à partir do [**cron** do Linux](http://www.cyberciti.biz/faq/how-do-i-add-jobs-to-cron-under-linux-or-unix-oses/).

Também podemos usar o comando `ps` para ver a árvore de processos com informações mais detalhadas.

Para ver os PIDs dos processos do tipo Apache:

    :::bash
    ps aux | grep apache | grep -v grep
    > www-data 17266  0.0  0.2 229916  6792 ?        S    16:14   0:00 /usr/sbin/apache2 -k start
    > root     22027  0.0  0.3 229808 10828 ?        Ss   16:01   0:00 /usr/sbin/apache2 -k start
    > www-data 22030  0.0  0.2 230264  7272 ?        S    16:01   0:00 /usr/sbin/apache2 -k start
    > www-data 22031  0.0  0.2 230280  7300 ?        S    16:01   0:00 /usr/sbin/apache2 -k start
    > www-data 22032  0.0  0.2 229940  7296 ?        S    16:01   0:00 /usr/sbin/apache2 -k start
    > www-data 22033  0.0  0.2 229880  7028 ?        S    16:01   0:00 /usr/sbin/apache2 -k start
    > www-data 22034  0.0  0.2 229880  7028 ?        S    16:01   0:00 /usr/sbin/apache2 -k start
    > www-data 28571  0.0  0.2 229880  6776 ?        S    16:04   0:00 /usr/sbin/apache2 -k start

Nesta execução, novos processos Apache filhos haviam sido criados no sistema. Vemos que o processo master possui **PID 22027**.

O comando abaixo irá mostrar a árvore de processos de uma forma mais detalhada:

    :::bash
    ps uf -p 22027,17266,22030,22031,22032,22033,22034,28571
    > USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
    > root     22027  0.0  0.3 229808 10828 ?        Ss   16:01   0:00 /usr/sbin/apache2 -k start
    > www-data 22030  0.0  0.2 230264  7272 ?        S    16:01   0:00  \_ /usr/sbin/apache2 -k start
    > www-data 22031  0.0  0.2 230280  7300 ?        S    16:01   0:00  \_ /usr/sbin/apache2 -k start
    > www-data 22032  0.0  0.2 229940  7296 ?        S    16:01   0:00  \_ /usr/sbin/apache2 -k start
    > www-data 22033  0.0  0.2 230268  7528 ?        S    16:01   0:00  \_ /usr/sbin/apache2 -k start
    > www-data 22034  0.0  0.2 229880  7028 ?        S    16:01   0:00  \_ /usr/sbin/apache2 -k start
    > www-data 28571  0.0  0.2 229880  7032 ?        S    16:04   0:00  \_ /usr/sbin/apache2 -k start
    > www-data 17266  0.0  0.2 229916  6792 ?        S    16:14   0:00  \_ /usr/sbin/apache2 -k start
    
Uma dica mais avançada para obter a mesma árvore é através do comando abaixo, obtido em um [post no Stack Overflow](http://stackoverflow.com/a/5311362). Este comando irá, a partir do PID do pai, mostrar todo o restante da árvore detalhadamente:

    :::bash
    ps uf -p $(pstree -p 22027 | sed 's/(/\n(/g' | grep '(' | sed 's/(\(.*\)).*/\1/' | tr "\n" " ")

Particulamente, gosto de usar o programa `htop` para analisar árvores de processos.

Processos órfãos
----------------

Um processo órfão é aquele em que o pai morreu, embora ele (o processo filho) continue executando.

Quando o pai de um processo morre, o comportamento comum do Linux é matar o processo pai, mantendo o filho executando, e associando o filho ao processo _init_. Chamamos o processo de órfão pois o seu pai original morreu, e ele foi adotado pelo processo _init_.

Em alguns casos, queremos que o filho continue executando: por exemplo, para iniciar deamons, para executar um processo independente do terminal TTY (por exemplo, usando o [comando `nohup`](http://www.cyberciti.biz/tips/nohup-execute-commands-after-you-exit-from-a-shell-prompt.html)), ou para aumentar a capacidade de recuperação de falhas de um sistema.

Em outros casos, gostaríamos que o filho também morresse. Para isso, o software deve ser programado para saber tratar esta situação.

Vamos simular agora o surgimento de um processo órfão. Para isso, vamos criar um programa que se duplica, criando um filho idêntico. Para isso, vamos criar um arquivo com o nome **fork.c**:

    #!c
    #include <unistd.h>
    #include <stdio.h>

    int main(int argc, char *argv[]) {
        pid_t pid;
    
        pid = fork();
        if (pid >= 0) { // fork successful
            if (pid != 0) { // parent
                printf("Parent process... Infinite loop\n");
            } else { // child
                printf("Child process... Infinite loop\n");
            }
            // infinite loop
            while (1) {
                sleep(5); // sleeping (low cpu usage)
            }   
        }
        return 0;
    }

Este processo criará um processo filho através de uma operação [_fork_](http://en.wikipedia.org/wiki/Fork_(system_call)). Depois, ambos os processos irão imprimir uma mensagem na tela. Ao executar o programa no shell do Linux, veremos ambas as mensagens, pois o processo filho herdará o terminal TTY do pai (veja [IBM - tty Special File](http://publib.boulder.ibm.com/infocenter/aix/v7r1/topic/com.ibm.aix.files/doc/aixfiles/tty.htm)). Como ambos os processos estarão executando simultaneamente, não podemos garantir a ordem que as mensagens irão aparecer, embora seja infinitamente mais provável que a mensagem do pai apareça primeiro.

Por fim, ambos entrarão em loop infinito. Este loop consumirá pouca CPU pois, na maior parte do tempo, os processos estarão em estado _sleeping_. 

Vamos compilar este programa usando o `gcc` e executá-lo:

    :::bash
    gcc -o fork fork.c
    ./fork
    > Parent process... Infinite loop
    > Child process... Infinite loop

Em outro terminal (pois o programa **fork** está rodando em _foreground_), iremos executar um `ps` para obter a árvore e os PIDs dos processos.

    :::bash
    ps af | grep -B 1 fork | grep -v grep
    > 20062 pts/0    S      0:00          \_ bash
    > 31351 pts/0    S+     0:00              \_ ./fork
    > 31352 pts/0    S+     0:00                  \_ ./fork

Neste exemplo, vemos que o **fork pai** possui como filho **outro fork** e como pai um processo **bash**.

Vamos, agora, matar o processo **fork pai** e verificar o que ocorre com o filho:

    :::bash
    kill -s SIGHUP 31351
    pstree -as 31352
    > init
    >   └─fork

O parâmetro `-s` passado ao pstree faz com que ele mostre somente os pais e filhos de um PID. Veja que, em muitos casos, podemos obter a mesma informação de diversas formas diferentes!

Agora, o processo **fork filho** virou um **processo órfão**, que possui como novo pai o processo **init**.

Por fim, iremos matar este processo para que ele não fique rodando no sistema.

    ::bash
    kill -s SIGHUP 31352

Criando processos running, sleeping e waiting
---------------------------------------------

Vamos criar 3 programas muito simples para demonstrar os estados mais comuns de processos. Vamos, depois, explicar o que eles fazem, executá-los, e ver o retorno do `ps`.

O primeiro programa será o **running.c**:

    #!c
    int main(int argc, char *argv[]) {
        while (1) { } // infinite loop
        return 0; 
    }   

Esse programa é muito simples: apenas executa um loop infinito.

O segundo programa será o **sleeping.c**:

    #!c
    #include <unistd.h>
    #include <limits.h>

    int main(int argc, char *argv[]) {
        sleep(UINT_MAX); // sleeeeeeeeeeping
        return 0;
    }   

Este programa dormirá pelo máximo de tempo possível, pois usamos o [máximo valor de _unsigned int_](http://www.cplusplus.com/reference/climits/), que é o [tipo de argumento recebido pela função `sleep`](http://www.gnu.org/software/libc/manual/html_node/Sleeping.html).

O terceiro programa será o **waiting.c**:

    #!c
    #include <unistd.h>
    #include <stdio.h>
    #include <sys/file.h>
    
    int main(int argc, char *argv[]) {
        pid_t pid = 0;
        const char* FILENAME = "waiting_file.txt";
        FILE *f; // file descriptor
        
        pid = fork();
        if (pid >= 0) { // fork successful
            if (pid != 0) { // parent
                f = fopen(FILENAME, "w");
                // See: http://stackoverflow.com/a/7573369
                flock(fileno(f), LOCK_EX); // locking the file
                while (1) { } // infinite loop
            } else { // child
                sleep(2); // forcing parent to execute before
                f = fopen(FILENAME, "w");
                flock(fileno(f), LOCK_EX); // waiting for I/O - deadlock here
                while (1) { } // infinite loop - only will execute if parent dead            
            }
        }
        fclose(f); // never executed
        return 0;
    }
    
Este programa criará outro processo filho. O processo pai dará um [_lock_](http://en.wikipedia.org/wiki/Lock_(computer_science)) em um arquivo e entrará em loop infinito. O processo filho tentará obter o lock para o mesmo arquivo e, por este motivo, ficará eternamente esperando por I/O. Teremos, assim, um _deadlock_.

Agora, vamos executar os três processos em _background_ (assim obtemos mais rapidamente o PID e não seremos obrigados a abrir vários shells).

    :::bash
    ./running &
    > [1] 11074
    ./sleeping &
    > [2] 11115
    ./waiting &
    > [3] 11438

Lembra que o programa *waiting* cria um filho ao realizar um _fork_? Vamos usar o `pstree` para obter o PID deste filho também:

    :::bash
    pstree -ap 11438
    > waiting,11438
    > └─waiting,11439

Agora, vamos utilizar o programa `ps` para verificar o estado de cada um dos processos:

    :::bash
    ps f -o pid,%cpu,state,command -p 11074,11115,11438,11439
    >   PID %CPU S COMMAND
    > 11438 42.1 R ./waiting
    > 11439  0.0 S  \_ ./waiting
    > 11115  0.0 S ./sleeping
    > 11074 45.4 R ./running

O parâmetro `-o` nos permite especificar as informações que queremos na saída do commando.

Neste output, podemos destacar dois pontos:

- Conseguimos obter processos com diversos estados:
    - O primeiro **running** possui estado _running_ (R);
    - O **sleeping** possui estado _sleeping_ (S);
    - O **waiting** pai e o filho possuem, respectivamente, os estados _running_ e _waiting_ (o segundo está esperando por I/O, que também é representado pela letra _S_ no output do `ps`);
- Os programas que estão em looping infinito estão consumindo muita CPU, ao passo que os outros apenas aguardam pacientes, sem consumir nenhuma CPU do sistema.

Para deixar a experiência mais legal ainda, vamos matar o processo **waiting** pai. Conforme já explicado, o processo filho passará a ser um processo órfão (filho de **init**):

    :::bash
    kill -s SIGHUP 11438
    ps f -o pid,%cpu,state,command -p 11438,11439
    >   PID %CPU S COMMAND
    > 11439 37.0 R ./waiting

Neste momento, o segundo processo **waiting** irá obter o lock do arquivo (pois, ao finalizar o primeiro processo, o sistema operacional liberará os recursos obtidos por este, incluindo o lock) e mudará seu estado para _running_. Na sequência, o processo entrará em loop infinito, consumindo bastante CPU.

Com a experiência finalizada, vamos matar todos os processos, para não deixá-los executando indefinidamente no sistema:

    :::bash
    killall running
    killall waiting
    killall sleeping

Enviando stop e resume para processos
-------------------------------------

Vamos agora apresentar os métodos principais para deixar um processo em estado _suspended_ (ou _stopped_).

O primeiro é digitando a combinação de teclas `CTRL+Z` no terminal. Ao receber este comando, o **bash** enviará um sinal para o programa executando em _foreground_, que irá parar a execução e entrar em estado _suspended_. 

O segundo método é mais genérico, e consiste no envio de sinais (através do programa `kill`) para o programa (veja [Sending signals to process](http://bash.cyberciti.biz/guide/Sending_signal_to_Processes)).

Vamos rodar, mais uma vez, o programa **running** em _background_:

    ./running &
    > [1] 11440

Agora, iremos enviar um [sinal SIGSTOP](http://major.io/2009/06/15/two-great-signals-sigstop-and-sigcont/) para este processo:

    :::bash
    kill -s SIGSTOP 11440

Vamos, agora, executar o comando `ps` para verificar o estado deste processo:

    :::bash
    ps -o pid,%cpu,state,command -p 11440
    >   PID %CPU S COMMAND
    > 11440  0.0 T ./running

Vemos que **running** agora possui estado _suspended_ (T), e não consome CPU do sistema operacional.

Ao enviar um sinal SIGCONT, este processo tornará a executar do ponto em que parou:

    :::bash
    kill -s SIGCONT 11440
    ps -o pid,%cpu,state,command -p 11440
    >   PID %CPU S COMMAND
    > 11440 82.7 R ./running

Referências
-----------

- [Linux process states](https://idea.popcount.org/2012-12-11-linux-process-states/)
- [Wikipedia - Orphan process](http://en.wikipedia.org/wiki/Orphan_process)
- [Silberschatz, Galvin e Gagne; Sistemas Operacionais com Java (Operating System Concepts with Java)](http://www.amazon.com/Operating-System-Concepts-Abraham-Silberschatz/dp/047050949X)

