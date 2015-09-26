Title: Processos zumbis: Tratando corretamente (parte 2)
Date: 2014-05-04 16:00
Tags: linux, shell, c, processos, zumbis
Slug: processos-zumbis-2
Category: Linux
Author: Rarylson Freitas
Summary: Saiba como evitar que seu software gere processos zumbis. Neste artigo, iremos desenvolver corretamente programas em C que não geram processos zumbis. Iremos apresentar alguns exemplos, em nível crescente de complexidade, visando a implementação eficiente do tratamento de processos zumbis.

No primeiro artigo [Processos zumbis: Introdução (parte 1)]({filename}processos-zumbis.md), mostramos o que são processos zumbis e quais são os problemas que eles podem causar.

Neste artigo, iremos mostrar como evitá-los: mostraremos como desenvolver uma aplicação que execute continuamente criando vários filhos, porém sem gerar um número crescente de processos zumbis, tratando-os de forma eficiente.

Recapitulando
-------------

Dentre os conceitos mais importantes do [artigo passado]({filename}processos-zumbis.md), podemos citar:

- Processo zumbis, também chamados de _zombies_ ou _defuncts_, são processos que terminaram a execução, tiveram seus recursos desalocados, mas ainda possuem uma entrada na tabela de processos;
- Em grande número, podem esgotar o número de PIDs do sistema ou o número máximo de processos que um usuário pode executar;
- Os processos, ao finalizarem sua execução, permanecem na tabela de processos para que seu processo pai possa ser notificado do fim de sua execução, analisar o código que o filho retornou, e executar ações necessárias para manter o correto funcionamento da aplicação.

Por que manter uma entrada na tabela de processos?
--------------------------------------------------

Sabemos que os processos zumbis existem para que um processo pai possa verificar o código retornado por seu processo filho. Mas, é realmente necessário manter estes processos na tabela do sistema? Não seria possível armazenar estas informações em outro lugar, liberando uma entrada da tabela de processos e evitando o esgotamento do PIDs?

**Obs:** Esta dúvida pode ser encontrada em alguns fóruns na internet, como [nesta pergunta encontrada no Stack Overflow](http://stackoverflow.com/questions/8665642/why-do-i-have-to-wait-for-child-processes).

Entretanto, existe uma [razão simples](http://stackoverflow.com/a/8669160/2530295) para que o processo finalizado continue na tabela de processos como um zumbi: caso isso não fosse feito, não haveria como identificar unicamente este processo. Ao liberar a entrada, o PID tornaria-se disponível para uso por outro processo, e deixaria de haver uma forma de identificar unicamente o processo que terminou a execução.

Tratando corretamente processos zumbis
--------------------------------------

Para mostrar diversas formas de tratar processos zumbis, iremos desenvolver um programa que rodará indefinidamente no sistema, gerando de tempos em tempos novos filhos. Após a execução de cada filho, este programa irá verificar o retorno da execução destes, contando quantas operações foram executadas com sucesso e quantas com falha.

Para implementar este exemplo, iremos utilizar dois programas: o pai, que lancará filhos e analisará os códigos de retorno, e os filhos, que terão comportamento probabilístico, podendo retornar valores diferentes em cada execução.

### Processo filho com comportamento aleatório

Iremos utilizar o [programa **maybe\_it\_works.c**](/programas-comportamento-aleatorio/#simulando-um-comportamento-aleatorio-em-c) (apresentado no artigo [Programas com Comportamento Aleatório: Introdução (parte 1)]({filename}./../programacao/programas-comportamento-aleatorio.md)) como processo filho.

O programa **maybe\_it\_works.c** utiliza funções aleatórias para simular dois comportamentos típicos de um programa real: tempo de processamento e ocorrência de erros. Em resumo, o programa:

- Utiliza a função `sleep` para simular seu tempo de execução. No caso, nosso programa poderá demorar 1, 2, 3 ou 4 segundos executando, cada tempo de execução com igual probabilidade de ocorrência;
- Retorna falha (código de retorno, ou _exit status_, diferente de zero) com probabilidade de 25%.

Agora, vamos compilar e testar este programa:

    :::console
    $ gcc -o maybe_it_works maybe_it_works.c
    $ time ./maybe_it_works
    real	0m2.001s
    user	0m0.004s
    sys	0m0.000s
    $ echo $?
    0

No teste realizado, **maybe\_it\_works** demorou 2 segundos para executar e retornou sucesso. Entretanto, ele poderia ter tido um tempo de execução diferente, ou mesmo ter retornado um valor diferente de zero.

### Tratando processos zumbis de forma síncrona

Vamos considerar o programa **keep\_calm.c**:

    #!c
    #include <unistd.h>
    #include <stdlib.h>
    #include <stdio.h>
    #include <sys/wait.h>
    
    #define PAUSE_BETWEEN_LAUNCHES 1
    #define CHILD_PATH "./maybe_it_works"

    int main(int argc, char *argv[]) {
        pid_t pid = 0;
        int status = 0;
        int errors = 0; // children that finished with errors
        int total = 0; // total of children that finished
        float percent = 0;        
         
        while (1) { // indefinidely fork and exec children
            sleep(PAUSE_BETWEEN_LAUNCHES);
            pid = fork();
            if (pid >= 0) { // fork successful
                if (pid != 0) { // parent
                    wait(&status); // wait until child die
                    // update counters
                    if (WIFEXITED(status) && WEXITSTATUS(status) != EXIT_SUCCESS) {
                        errors++;
                    }   
                    total++;
                    // print statistics
                    percent = (float)(errors) / total * 100;
                    printf("Errors: %d, Total: %d, Percent: %.2f%%\n", errors, total, 
                            percent);
                } else { // child
                    if (! execl(CHILD_PATH, CHILD_PATH, (char *)(NULL))) { // exec child program
                        printf("Error on exec\n");
                        exit(EXIT_FAILURE);
                    }
                }   
            } else {
                printf("Error on fork\n");
            }   
        }   
         
        return 0;
    }

Este programa roda indefinidamente no sistema através da execução de um loop, executando a seguinte lógica a cada iteração:

- Inicialmente, ele fica em estado _sleep_ durante o intervalo de tempo `PAUSE_BETWEEN_LAUNCHES`;
- Em seguida, executa um _fork_, gerando um processo filho;
- O processo filho carrega e executa (operação _exec_) o programa **maybe_it_works**;
- O processo pai, por sua vez, realiza uma operação _wait_, aguardando a execução do processo filho e obtendo o status de sua execução;
- Após o retorno da operação _wait_, o processo pai verifica o status do processo filho e atualiza seus contadores (número total de processos filhos executados e número de filhos que retornaram erro);
- Por fim, o pai imprime na tela seus contadores, retornando ao início do loop.

A geração do processo filho é realizada através da técnica [fork-exec](http://en.wikipedia.org/wiki/Fork-exec) e consiste em duas partes.

A primeira etapa é o `fork` (linha 18), que gera um processo filho clone do processo pai. Depois da operação, ambos os processos continuam a execução do mesmo ponto, [existindo apenas poucas diferenças entre eles](http://linux.die.net/man/2/fork) (por exemplo, o PID e o valor retornado pela função `fork`).

Já a segunda é a operação _exec_, no nosso caso implementada através de uma chamada à função `execl` (linha 32), cujo protótipo é apresentado abaixo:

    :::c
    int execl(const char *path, const char *arg, ...);

Esta função substitue a imagem do processo em execução (código, variáveis, etc) por uma nova imagem de processo. Seu primeiro argumento é a localização do código a ser executado, que pode ser um arquivo binário com instruções executáveis (nosso caso) ou um script interpretável. 

Já os demais parâmetros são passados ao "novo processo" como uma lista de parâmetros de linha de comando. Por convenção, o primeiro parâmetro a ser passado deve ser o nome do arquivo que contém o código a ser executado/interpretado. O último parâmetro a ser parado para `execl` precisa ser um ponteiro nulo (_null pointer_).

**Obs:** A função `execl` é apenas uma das que compõem a [família de funções exec](http://man7.org/linux/man-pages/man3/exec.3.html). Embora elas difiram entre si em alguns detalhes, todas são utilizadas para carregar um novo código.

Outro detalhe a ser observado no nosso programa é a chamada a [função `wait`](http://linux.die.net/man/2/wait), onde o pai aguarda de forma síncrona mudanças no estado do processo filho (como o fim de sua execução) armazenando na variável `status` várias informações relacionadas ao evento ocorrido.

O valor armazenado na variável `status` possui várias informações. Entretanto, existem várias macros que podem ser utilizadas para facilitar a interpretação desta variável. No nosso caso, testamos se a mudança de estado ocorrida foi o fim da execução do processo filho (macro `WIFEXITED`) e verificamos o código de retorno do processo filho (macro `WEXITSTATUS`).

Vamos, agora, compilar e testar o nosso programa. Devemos executá-lo no mesmo diretório que reside o programa **maybe\_it\_works**.

    :::console
    $ gcc -o keep_calm keep_calm.c
    $ ./keep_calm 
    Errors: 1, Total: 1, Percent: 100.00%
    Errors: 1, Total: 2, Percent: 50.00%
    Errors: 2, Total: 3, Percent: 66.67%
    [...]
    Errors: 5, Total: 21, Percent: 23.81%
    Errors: 5, Total: 22, Percent: 22.73%
    Errors: 6, Total: 23, Percent: 26.09%

Vemos que, após inúmeras execuções, o número de execuções com erro tende a ficar próximo a 25%, conforme esperado.

Vamos agora abrir outro terminal e verificar o status dos nossos processos:

    :::console
    $ ps aux | grep -e keep_calm -e maybe_it_works | grep -v grep
    root     20480  0.0  0.0   4204   520 pts/3    S+   13:44   0:00 ./keep_calm
    root     22428  0.0  0.0   4200   364 pts/3    S+   14:24   0:00 ./maybe_it_works

Aguardando mais alguns instantes e repetindo a experiência:

    :::console
    $ ps aux | grep -e keep_calm -e maybe_it_works | grep -v grep
    root     20480  0.0  0.0   4204   520 pts/3    S+   13:44   0:00 ./keep_calm
    root     22456  0.0  0.0   4200   364 pts/3    S+   14:26   0:00 ./maybe_it_works 

Vemos o mesmo processo pai em ambos os testes (PID 20480), porém processos filhos diferentes (PIDs 22428 e 22456). Além disso, vemos que sempre há 2 processos executando, não havendo nenhum processo zumbi.

### Tratando processos zumbis sem esperas

O programa **keep\_calm.c** tem algumas limitações: ele executa somente um processo filho por vez e fica ocioso enquanto aguarda este processo filho terminar. Este modelo desperdiça recursos computacionais.

Para solucionar esta limitação, vamos apresentar uma versão otimizada do nosso programa anterior, que chamaremos de **dont\_keep\_calm.c**. 
Para isso, iremos utilizar o programa anterior como base e alterar algumas linhas de código.

Vamos, então, substituir as linhas de 21 a 26 do nosso programa original pelo trecho abaixo:

    :::c
    while(waitpid(-1, &status, WNOHANG) > 0) { // loop through all died children
        // update counters
        if (WIFEXITED(status) && WEXITSTATUS(status) != EXIT_SUCCESS) {
            errors++;
        }   
        total++;
    }

Também devemos substituir a linha onde calculamos a porcentagem (linha 28):

    :::c
    percent = (total != 0) ? (float)(errors) / total * 100 : 0;

Estamos agora utilizando a [função `waitpid`](http://linux.die.net/man/2/wait), que provê novas funcionalidades quando comparada à função `wait`. Seu protótipo é apresentado abaixo:

    :::c
    pid_t waitpid(pid_t pid, int *status, int options);

Algumas características desta função são:

- O primeiro argumento, se maior que zero, fará com que esta função aguarde um processo que possui um PID específico. Entretanto, se for passado o valor -1 como argumento, `waitpid` aguardará por qualquer filho, exatamente como faz a função `wait`;
- O terceiro argumento aceita opções que mudam o comportamento da função. Dentre elas, podemos citar a constante `WNOHANG`, que faz com que a função retorne imediatamente caso nenhum filho tenha finalizado;
    - As opções devem ser passados através de um operador _or bitwise_, como em `WNOHANG | WCONTINUED`;
- Em caso de sucesso, a função retorna o PID do processo que mudou o estado;
    - Se a opção `WNOHANG` for passada e não existirem processos filhos a serem tratados, `waitpid` retornará zero.

**Obs:** `wait(&status)` e `waitpid(-1, &status, 0)` são comandos equivalentes.

Em cada interação do loop principal, `waitpid` será executada enquanto houver processos zumbis a serem tratados. Por exemplo, se houver 2 processos zumbis na tabela de processos do sistema, `waitpid` executará 3 vezes, atualizando seus contadores nas duas primeiras execuções, e saindo do loop na terceira execução.

Já a mudança do cálculo da porcentagem foi necessária para evitarmos um erro de divisão por zero: durante as primeiras execuções do programa, pode ainda não existirem processos finalizados (`total` igual a zero).

Vamos agora compilar e testar o nosso programa:

    :::console
    $ gcc -o dont_keep_calm dont_keep_calm.c
    ./dont_keep_calm 
    Errors: 0, Total: 0, Percent: 0.00%
    Errors: 0, Total: 0, Percent: 0.00%
    Errors: 0, Total: 0, Percent: 0.00%
    Errors: 1, Total: 1, Percent: 100.00%
    Errors: 2, Total: 2, Percent: 100.00%
    [...]
    Errors: 5, Total: 17, Percent: 29.41%
    Errors: 5, Total: 17, Percent: 29.41%
    Errors: 5, Total: 19, Percent: 26.32%
    Errors: 5, Total: 20, Percent: 25.00%

Neste teste, podemos ver que:

- Nas duas primeiras execuções, ainda não havia nenhum processo filho finalizado;
- Em um dado momento, o número total de processos finalizados permaneceu constante (17) entre duas iterações;
    - O programa não aguarda por processos filhos de forma bloqueante. Assim, se nenhum processo filho finalizou, o processo pai irá imprimir os mesmos valores da iteração anterior e continuar com a execução;
- No instante seguinte, este número subiu de 17 para 19;
    - Nosso programa pode lançar vários processos filhos em paralelo. Além disso, ele apenas trata os processos zumbis de tempos em tempos. Assim, caso tenhamos, em um dado momento, 2 processos filhos executando em paralelo e caso eles terminem sua execução quase ao mesmo tempo, o processo pai irá analisar ambos na mesma iteração. 

Assim como no exemplo anterior, vamos abrir outro terminal e verificar o status dos processos:

    :::console
    $ ps aux | grep -e dont_keep_calm -e maybe_it_works | grep -v grep
    root     24565  0.0  0.0   4204   516 pts/3    S+   17:15   0:00 ./dont_keep_calm
    root     24592  0.0  0.0   4200   368 pts/3    S+   17:15   0:00 ./maybe_it_works
    root     24593  0.0  0.0   4200   368 pts/3    S+   17:15   0:00 ./maybe_it_works

Após aguardar alguns instantes, vamos repetir novamente o comando anterior:

    :::console
    $ ps aux | grep -e dont_keep_calm -e maybe_it_works | grep -v grep
    root     24565  0.0  0.0   4204   516 pts/3    S+   17:15   0:00 ./dont_keep_calm
    root     24708  0.0  0.0   4200   368 pts/3    S+   17:17   0:00 ./maybe_it_works
    root     24709  0.0  0.0      0     0 pts/3    Z+   17:17   0:00 [maybe_it_works] <defunct>
    root     24713  0.0  0.0   4200   368 pts/3    S+   17:17   0:00 ./maybe_it_works
    root     24723  0.0  0.0   4200   368 pts/3    S+   17:17   0:00 ./maybe_it_works

Vemos que:

- Em ambos os testes, existiam processos filhos executando em paralelo;
- No último teste, um processo zumbi foi listado;
    - Como o nosso processo pai verifica processos zumbis apenas de 1 em 1 segundo (`PAUSE_BETWEEN_LAUNCHES`), sempre é possível que existam processos zumbis no sistema neste intervalo de tempo.

### Tratando processos zumbis usando sinais

O programa apresentado anteriormente trouxe avanços ao não realizar chamadas _wait_ bloqueantes. Ainda assim, existem pontos que podem ser melhorados, deixando nosso programa mais eficiente:

- Em alguns casos, `waitpid` é executada inutilmente, mesmo que não haja processos zumbis a serem tratados;
- Um processo zumbi pode existir no sistema durante até 1 segundo (`PAUSE_BETWEEN_LAUNCHES`).

Visando implementar estas melhorias, iremos desenvolver um novo programa chamado de **work\_hard\_play\_hard.c**:

    #!c
    #include <unistd.h>
    #include <stdlib.h>
    #include <stdio.h>
    #include <sys/wait.h>
    
    #define PAUSE_BETWEEN_LAUNCHES 2
    #define CHILD_PATH "./maybe_it_works"
    
    // process SIGCHLD signals
    static void sigchld_handler(int signum) {
        static int errors = 0; // children that finished with errors
        static int total = 0; // total of children that finished
        float percent = 0;
        int status = 0;
        
        // loop through all died children
        while(waitpid(-1, &status, WNOHANG) > 0) {
            // update counters
            if (WIFEXITED(status) && WEXITSTATUS(status) != EXIT_SUCCESS) {
                errors++;
            }
            total++;
        }   
        // print statistics
        percent = (total != 0) ? (float)(errors) / total * 100 : 0;
        printf("Errors: %d, Total: %d, Percent: %.2f%%\n", errors, total, percent);
    }
    
    int main(int argc, char *argv[]) {
        pid_t pid = 0;
        int sleep_remaining = 0; // remaining time to sleep
    
        // set handler to SIGCHLD
        if (signal(SIGCHLD, sigchld_handler) == SIG_ERR) {
            printf("Error while setting a signal handler\n");
            exit(EXIT_FAILURE);
        }   
    
        while (1) { // indefinidely fork and exec children
            // sleep the expected time, even if an interruption occurs
            sleep_remaining = PAUSE_BETWEEN_LAUNCHES;
            while ((sleep_remaining = sleep(sleep_remaining)) > 0) { }
            pid = fork();
            if (pid >= 0) { // fork successful
                if (pid == 0) { // child
                    if (! execl(CHILD_PATH, CHILD_PATH, (char *)(NULL))) { // exec child program
                        printf("Error on exec\n");
                        exit(EXIT_FAILURE);
                    }
                }
            } else {
                printf("Error on fork\n");
            }
        }
    
        return 0;
    }

Quando um processo filho termina sua execução, [ele envia ao pai um sinal (ou _signal_) **`SIGCHLD`**](http://docs.oracle.com/cd/E19455-01/806-4750/signals-7/index.html). Por este motivo, definimos a função `sigchld_handler` como _handler_ do sinal **`SIGCHLD`**. É nesta função que faremos o tratamento dos processo zumbis.

**Obs:** A utilização de sinais é uma forma de comunicação entre processos assíncrona e baseada em eventos. O artigo [Enviando e tratando sinais em processos Linux]({filename}processos-sinais.md) explica vários aspectos relacionados ao envio de sinais e ao uso de _signal handlers_.

Com este novo modelo, conseguimos as seguintes melhorias:

- Otimizamos o tempo de processamento de nossa aplicação, pois `waitpid` apenas é chamada quando necessário;
- Tratamos processos zumbis de forma mais rápida pois, assim que o filho termina (e o sinal `SIGCHLD` é recebido), realizamos rapidamente seu processamento.  

As variáveis `errors` e `total`, agora, são definidas como variáveis estáticas. Em C, [variáveis estáticas](http://en.wikipedia.org/wiki/Static_variable) são variáveis cujo tempo de vida é igual ao tempo de execução do programa (assim como ocorrem com variáveis globais), mas possuem escopo local.

Também houve uma mudança na implementação da funcionalidade _sleep_. Esta mudança levou em conta que [a função `sleep` também retorna após ser interrompida para o tratamento de um sinal (_signal handler_)](http://stackoverflow.com/questions/14266485/understanding-sigchld-when-the-child-process-terminates/14266622#14266622). Ao ser interrompida para que um sinal seja tratado, a função retornará quantos segundos ainda restam para completar o tempo especificado em sua chamada. Nós utilizamos este valor retornado em um loop para garantir que tornaremos a executar `sleep` até que todo o tempo `PAUSE_BETWEEN_LAUNCHES` (alterado para 2 segundos nesta experiência) seja alcançado.

**Obs:** A função `sleep` recebe e retorna números inteiros. Caso seja necessário uma precisão maior, fazendo com que o loop de operações `sleep` execute um valor muito próximo do tempo especificado, pode-se utilizar a função `nanosleep`. Este [artigo no _cc.byexamples.com_](http://cc.byexamples.com/2007/05/25/nanosleep-is-better-than-sleep-and-usleep/) apresenta um interessante exemplo de uso desta função.

Vamos, agora, compilar e testar nosso programa:

    :::console
    $ gcc -o work_hard_play_hard work_hard_play_hard.c
    $ ./work_hard_play_hard
    Errors: 0, Total: 1, Percent: 0.00%
    Errors: 1, Total: 2, Percent: 50.00%
    Errors: 2, Total: 3, Percent: 66.67%
    Errors: 2, Total: 4, Percent: 50.00%
    [...]
    Errors: 9, Total: 23, Percent: 39.13%
    Errors: 11, Total: 25, Percent: 44.00%
    [...]
    Errors: 16, Total: 65, Percent: 24.62%

Analisando o resultado, vemos que:

- Em nenhum momento entre duas execuções o número total de processos finalizados se manteve constante;
    - Isso mostra que temos um melhor aproveitamento de CPU ao chamar `waitpid`;
- O nosso processo trata processos zumbis tão logo recebe o sinal SIGCHLD. Assim, um incremento maior que 1 no número total de processos passou a ser um evento raro;
    - No exemplo, isso apenas ocorreu uma vez (quando o número total passou de 23 para 25).

Vamos, agora, em um novo terminal, verificar o status dos processos em execução:

    :::console
    $ ps aux | grep -e work_hard_play_hard -e maybe_it_works | grep -v grep
    root     12200  0.0  0.0   4204   520 pts/3    S+   22:53   0:00 ./work_hard_play_hard
    root     12450  0.0  0.0   4200   368 pts/3    S+   22:54   0:00 ./maybe_it_works
    root     12451  0.0  0.0   4200   364 pts/3    S+   22:54   0:00 ./maybe_it_works

Mesmo repetindo este comando inúmeras vezes, vemos que é muito difícil a ocorrência de um processo zumbi, visto que nosso programa os trata quase que imediatamente após aparecerem.

O que ainda falta?
------------------

No [primeiro artigo]({filename}processos-zumbis.md) sobre processos zumbis, mostramos que tipos de problemas eles podem causar: como eles podem esgotar o número máximo de processos de um usuário ou mesmo o número de PIDs do sistema.

Neste artigo, mostramos como implementar corretamente softwares que tratam processos seus processos filhos finalizados, evitando o acúmulo de processos zumbis no sistema.

Em um outro artigo, iremos apresentar uma experiência real. Iremos mostrar uma situação na qual um software não tratava corretamente seus processos zumbis, bem como iremos mostrar as ações realizadas para diagnosticar e solucionar o problema.

Referências
-----------

- [Wikipedia - Zombie Process](http://en.wikipedia.org/wiki/Zombie_process)
- [Signals (and Zombie and SIGCHLD)](http://www.win.tue.nl/~aeb/linux/lk/lk-5.html)
- [Linux Processes – Process IDs, fork, execv, wait, waitpid C Functions](http://www.thegeekstuff.com/2012/03/c-process-control-functions/)
- [Wait system calls - Linux man page](http://linux.die.net/man/2/wait)
- [The exec() family of functions - Linux man page](http://linux.die.net/man/3/exec)
