Title: Processos zumbis: Tratando corretamente (parte 2)
Date: 2014-01-26 18:10
Tags: linux, shell, c, processos, zumbis, real
Slug: processos-zumbis-2
Category: Linux
Author: Rarylson Freitas
Summary: Saiba como evitar que seu software gere processos zumbis. Neste artigo, iremos desenvolver corretamente programas em C que não geram processos zumbis. Iremos também analisar como alguns softwares do mundo real tratam este tipo de processo. Por fim, iremos apresentar um exemplo real de software onde uma falha permitia criar infindandamente processos zumbis no sistema.
Status: draft

No primeiro artigo [Processos zumbis: Introdução (parte 1)]({filename}processos-zumbis.md), mostramos o que são processos zumbis e quais são os problemas que eles podem causar.

Neste artigo, iremos mostrar como evitá-los: mostraremos como desenvolver uma aplicação que execute continuamente criando vários filhos, porém sem gerar um número crescente de processos zumbis.

Iremos também apresentar como alguns softwares reais tratam processos zumbis.

Por fim, iremos mostrar um exemplo real no qual o software **Symantec Backup Exec**, em uma versão mais antiga, não trata corretamente o fim de seus processos filhos, gerando vários processos zumbis no sistema. Iremos mostrar também o _workarround_ utilizado para contornar a situação.

[TOC]

Recaptulando
------------

Dentre os conceitos mais importantes do [artigo passado]({filename}processos-zumbis.md), podemos citar:

- Processo zumbis, também chamados de _zombies_ ou _defuncts_, são processos que terminaram a execução, tiveram seus recursos desalocados, mas ainda possuem uma entrada na tabela de processos;
- Em grande número, podem esgotar o número de PIDs do sistema, ou mesmo esgotar o número máximo de processos que um usuário pode executar;
- Os processos, ao finalizarem sua execução, permanecem na tabela de processos para que seu processo pai possa ser notificado do fim de sua execução, analisar o código que o filho retornou, e executar ações necessárias para manter o correto funcionamento da aplicação;
    - Assim, _deamons_ deveriam tratar corretamente seus processos filhos, retirando adequadamente suas entradas da tabela de processos a medida que estes vão finalizando sua execução.

Porque manter uma entrada na tabela de processos?
-------------------------------------------------

Sabe-se que os processos zumbis existem para que seu processo pai possa verificar o código retornado por seu processo filho. Mas, é realmente necessário manter estes processos na tabela do sistema? Não seria possível armazenar estas informações em outro lugar, liberando uma entrada da tabela de processos e evitando o esgotamento do PIDs?

**Obs:** Esta dúvida pode ser encontrada em alguns fóruns na internet, como [nesta pergunta aqui](http://stackoverflow.com/questions/8665642/why-do-i-have-to-wait-for-child-processes), encontrada no Stack Overflow.

Entretanto, existe uma [razão simples](http://stackoverflow.com/a/8669160/2530295) para que o processo finalizado continue na tabela de processos como um zumbi: caso isso não fosse feito, não haveria como identificar unicamente este processo. Ao liberar a entrada, o PID tornaria-se disponível para uso por outro processo, e deixaria de haver uma forma de identificar unicamente o processo que terminou a execução.

Tratando corretamente processos zumbis
--------------------------------------

Vamos considerar um exemplo genérico de um programa que rodará indefinidamente no sistema gerando filhos e verificando o retorno da execução destes, contando quantas operações foram executadas com sucesso ou falha.

Para isto, vamos fazer uso do programa em C **maybe\_it\_works.c**, apresentado no artigo [Programas com Comportamento Aleatório]({filename}./../programacao/programas-comportamento-aleatorio.md).

Foram apresentadas várias versões deste programa, mas iremos utilizar a [primeira delas](/programas-comportamento-aleatorio/#simulando-um-comportamento-aleatorio-em-c) neste artigo. Assim, vamos inicialmente criar este arquivo com o mesmo código da versão do link anterior. 

**Obs:** Você não precisa entender os detalhes de implementação deste programa para compreender os exemplos posteriores. Entretanto, caso queira compreender mais sobre ele, fique à vontade para ler o artigo citado.

O programa **maybe\_it\_works.c** utiliza funções aleatórias para simular dois comportamentos típicos de um programa real: tempo de processamento e ocorrência de erros. Em resumo, o programa:

- Utiliza a operação **sleep** para simular o tempo de execução do programa. No caso, nosso programa demorará 1s, 2s, 3s ou 4s executando, cada tempo de execução possuindo igual probabilidade de ocorrer;
- Nosso programa retorna falha (código de retorno, ou _exit status_, diferente de zero) com probabilidade de 25%.

Agora, iremos compilar e testar este programa:

    :::bash
    gcc -o maybe_it_works maybe_it_works.c
    time ./maybe_it_works
    > real	0m2.001s
    > user	0m0.004s
    > sys	0m0.000s
    echo $?
    > 0

A instrução `echo $?` imprime o código de retorno do último comando executado. No teste realizado, **maybe\_it\_works** retornou sucesso. Entretanto, convém lembrar que ele poderia ter retornado um valor diferente de zero com 25% de probabilidade.

### Tratando processos zumbis de forma síncrona

Inicialmente, vamos considerar o programa **keep\_calm.c**:

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
         
        while (1) { // indefinidely fork and exec children
            sleep(PAUSE_BETWEEN_LAUNCHES);
            pid = fork();
            if (pid >= 0) { // fork sucessful
                if (pid != 0) { // parent
                    wait(&status); // wait until child die
                    // update counters
                    if (WIFEXITED(status) && WEXITSTATUS(status) != EXIT_SUCCESS) {
                        errors++;
                    }   
                    total++;
                    // print statistics
                    printf("Errors: %d, Total: %d, Percent: %.2f%%\n", errors, total, 
                            (float)(errors) / total * 100);
                } else { // child
                    execl(CHILD_PATH, CHILD_PATH, (char *)(NULL)); // exec child program
                }   
            } else {
                printf("Error on fork\n");
            }   
        }   
         
        return 0;
    }

Explicar!

Explicar que status representa várias coisas, e que as funções WIFEXITED e WEXITSTATUS facilitam sua interpretação.

Testar o número de processos zumbis. Mostrar que sempre temos 2 processos executando.

### Tratando processos zumbis sem esperas

**modelo 2:** waitpid( -1, &status, WNOHANG ) dentro de um loop (lança um processo, pergunta se algum filho morreu, lança outro, pergunta novamente)

**work\_hard\_play\_hard.c**:

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
            if (pid >= 0) { // fork sucessful
                if (pid != 0) { // parent
                    // loop into all died children
                    while(waitpid(-1, &status, WNOHANG) > 0) {
                        // update counters
                        if (WIFEXITED(status) && WEXITSTATUS(status) != EXIT_SUCCESS) {
                            errors++;
                        }   
                        total++;
                    }   
                    // print statistics
                    percent = (total != 0) ? (float)(errors) / total * 100 : 0;
                    printf("Errors: %d, Total: %d, Percent: %.2f%%\n", errors, total, 
                            percent);
                } else { // child
                    execl(CHILD_PATH, CHILD_PATH, (char *)(NULL)); // exec child program
                }   
            } else {
                printf("Error on fork\n");
            }   
        }   
        
        return 0;
    }

Primeiramente, iremos apresentar uma função semelhante a função `wait`: a função `waipid` (também apresentada [no artigo do The Geek Stuff](http://www.thegeekstuff.com/2012/03/c-process-control-functions/)). Ela provê novas funcionalidades, permitindo, dentre outras coisas, aguardar um processo que possui um PID específico. Seu protótipo é apresentado abaixo:

    :::c
    pid_t waitpid(pid_t pid, int *status, int options);

As principais novidades são:

- O primeiro argumento, se maior que zero, representa o PID do processo aguardado, isto é, a função (em seu comportamento padrão) apenas irá retornar quando o processo com este PID mudar de estado. Entretanto, se for passado o valor -1 como argumento, `waitpid` aguardará por qualquer filho, semelhante a `wait`;
- O terceiro argumento aceita algumas opções que mudam o comportamento da função. Dentre eles, o mais interessante é o inteiro representado pela constante `WNOHANG`, que faz com que a função retorne imediatamente caso nenhum filho tenha finalizado;
    - As opções devem ser passados através de um **or** _bitwise_, como em `WNOHANG | WCONTINUED`.

**Obs:** `wait(&status)` e `waitpid(-1, &status, 0)` são comandos equivalentes.

Explicar o programa! Mostrar que podemos ter vários processos executando, que eles crescem indefinidamente (lancamos mais rápido do que eles acabam), mas explicar que muitas aplicações reais limitam o número máximo destes processos. Falar que, enquanto processos zumbis esgotam o número de PIDs, em situações reais, infinitos processos costumam esgotar a memória.

Exemplo: php-fpm e o max_clients.

### Tratando processos zumbis usando sinais

**modelo 3:** waitpid( -1, &status, WNOHANG ) usando sinais (apenas lança processos. tratar filhos mortos é feito por sinais)

**improved\_work\_hard\_play\_hard.c**:

    #!c
    #include <unistd.h>
    #include <stdlib.h>
    #include <stdio.h>
    #include <sys/wait.h>
    
    #define PAUSE_BETWEEN_LAUNCHES 1
    #define CHILD_PATH "./maybe_it_works"
    
    // process SIGCHLD signal
    static void sigchld_handler(int signum) {
        static int errors = 0; // children that finished with errors
        static int total = 0; // total of children that finished
        static float percent = 0;
        int status = 0;
        
        // loop into all died children
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
    
        // set handler to SIGCHLD
        if (signal(SIGCHLD, sigchld_handler) == SIG_ERR) {
            printf("Error while setting a signal handler\n");
            exit(EXIT_FAILURE);
        }   
    
        while (1) { // indefinidely fork and exec children
            sleep(PAUSE_BETWEEN_LAUNCHES);
            pid = fork();
            if (pid >= 0) { // fork sucessful
                if (pid == 0) { // child
                    execl(CHILD_PATH, CHILD_PATH, (char *)(NULL)); // exec child program
                }
            } else {
                printf("Error on fork\n");
            }
        }
    
        return 0;
    }


Falar do SIGCHLD.

http://superuser.com/questions/359599/why-is-my-dev-random-so-slow-when-using-dd

Como alguns programas reais tratam processos zumbis
---------------------------------------------------

1) Execução não demora muito. Não há necessidade de tratar
2) Fork and die (deamons) => Não precisa se preocupar com o que ocorre com o filho
3) Trata de tempo em tempo
4) Trata quase que instantaneamente

Exemplo real: Backup Exec e o aparecimento de processos zumbis
--------------------------------------------------------------

Ver email: Considerações sobre o Servidor Oracle

Referências
-----------

- [Wikipedia - Zombie Process](http://en.wikipedia.org/wiki/Zombie_process)
- [Signals (and Zombie and SIGCHLD)](http://www.win.tue.nl/~aeb/linux/lk/lk-5.html)
- [Linux Processes – Process IDs, fork, execv, wait, waitpid C Functions](http://www.thegeekstuff.com/2012/03/c-process-control-functions/)
- [Wait system calls - Linux man page](http://linux.die.net/man/2/wait)
- [The exec() family of functions - Linux man page](http://linux.die.net/man/3/exec)
