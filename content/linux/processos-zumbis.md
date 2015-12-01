Title: Processos zumbis: Introdução (parte 1)
Date: 2013-10-20 18:10
Tags: linux, shell, c, processos, zumbi
Slug: processos-zumbis
Category: Linux
Author: Rarylson Freitas
Summary: Entenda melhor o que são processos zumbis. Neste artigo, mostraremos como reproduzí-los através de experiências e programas em C, e você entenderá os motivos que podem levar a sua aparição em servidores e os problemas que podem causar.

Em um artigo anterior, chamado [Tipos de processos no Linux]({filename}processos-tipos.md), mostramos quais são os diversos tipos de processos e como funciona a hierarquia de processos no Linux.

Agora, iremos realizar diversas experiências para mostrar como podemos simular o aparecimento de processos zumbis, bem como os transtornos que podem causar.

Processos com estas características costumam surgir, muitas vezes, devido a falhas de programação ou operação incorreta do sistema operacional.

Processos zumbis 
----------------

Um [processo zumbi](http://en.wikipedia.org/wiki/Zombie_process) (ou _zombie_, chamado também de _defunct_) é um processo que finalizou a execução mas ainda possui uma entrada na tabela de processos, pois seu processo pai ainda não "tomou conhecimento" que ele terminou.

Os processos zumbis são assim chamados porque eles morreram (finalizaram a execução), tiveram seus recursos desalocados (memória, descritores de arquivo, etc), mas ainda não foram "expurgados" do sistema (permanece sua entrada na tabela de processos do sistema). Estão mortos, mas ainda existem de alguma forma no sistema.

A tabela de processos do sistema é importante para o funcionamento de [sistemas multitarefa](http://en.wikipedia.org/wiki/Computer_multitasking) (_multitasking_) e para a gerência dos processos (o `ps` e o `htop`, por exemplo, consultam esta tabela). Esta [resposta no Stack Overflow](http://stackoverflow.com/a/4880715/2530295) e [esta no Linux Forums](http://www.linuxforums.org/forum/kernel/42062-use-process-table.html) explicam sobre esta tabela.

O fato de um processo zumbi permanecer na tabela de processos faz com que:

- Uma quantidade pequena de memória permaneça alocada para manter esta entrada;
    - Como estas entradas ocupam pouca memória (considerando a capacidade dos computadores atuais), isto não costuma ser um problema;
- A tabela de processos cresça;
    - Dada a capacidade computacional dos hardwares atuais, isto apenas implicaria em mais processos a serem gerenciados, não sendo um grave problema;
- O PID usado pelo processo fique indisponível para reutilização;
    - Este geralmente é o maior problema causado por processos zumbis: em grande número, eles podem esgotar o número de processos que um usuário pode iniciar ou mesmo esgotar o número de PIDs do sistema.

### Por que eles devem existir?

Se processos zumbis ocupam PIDs, por que eles existem?

A razão é que, muitas vezes, o processo pai precisa tomar conhecimento que o filho morreu, saber qual [código este retornou](http://en.wikipedia.org/wiki/Exit_status), e executar alguma ação em função destas informações.

Por exemplo, um processo pai poderia ser configurado para controlar um certo número de processos filhos. Se um processo filho fosse encerrado abruptamente, o pai poderia "tomar conhecimento" que o filho morreu, armazenar em _log_ o código de erro retornado pelo filho, e iniciar um novo filho.

Vários softwares reais possuem comportamento semelhante ao descrito acima. Podemos citar o Nginx, que utiliza uma arquitetura _master_/_workers_, com número de _workers_ definido pela configuração [_worker_processes_](http://nginx.org/en/docs/ngx_core_module.html#worker_processes). Quando um _worker_ morre, o processo _master_ (pai de todos os _workers_), após algum tempo, inicia um novo _worker_.

Se você tem um Nginx instalado, teste você mesmo! Se for testar em um servidor em produção, recomendamos que [envie um SIGQUIT para que nenhum usuário seja prejudicado](http://wiki.nginx.org/CommandLine#Stopping_or_Restarting_Nginx). 

Criando processos zumbis
-----------------------

Vamos agora apresentar um programa que gerará filhos indefinidamente. Estes filhos irão imprimir uma mensagem na tela e, logo em seguida, terminar sua execução. Chamaremos este programa de **the_walking_dead.c**:

    #!c
    #include <unistd.h>
    #include <stdio.h>
    #include <stdlib.h>

    #define SLEEP_TIME 5

    int main(int argc, char *argv[]) {
        pid_t pid;

        while (1) { // indefinidely fork
            sleep(SLEEP_TIME); // creating childrens SLEEP_TIME to SLEEP_TIME seconds
            pid = fork();
            if (pid >= 0) { // fork successful
                if (pid == 0) { // child - print and exit
                    printf("Child created and ending... Bye!\n");
                    exit(EXIT_SUCCESS);
                }
            } else { // error
                printf("Error while forking\n");
            }
        }
        return 0;
    }

O programa acima irá gerar um novo filho de 5 em 5 segundos.
    
Agora, iremos compilar e rodar o processo. Veremos que, de tempos em tempos, uma nova mensagem será impressa na tela:

    :::console
    $ gcc -o the_walking_dead the_walking_dead.c
    $ ./the_walking_dead 
    Child created and ending... Bye!
    Child created and ending... Bye!
    Child created and ending... Bye!

Após alguns segundos, em outro terminal, iremos imprimir na tela os processos **the\_walking\_dead**:

    :::console
    $ ps aux | grep the_walking | grep -v grep
    rarylson 21768  0.0  0.0   4156   356 pts/0    S+   04:28   0:00 ./the_walking_dead
    rarylson 21883  0.0  0.0      0     0 pts/0    Z+   04:28   0:00 [the_walking_dea] <defunct>
    rarylson 22036  0.0  0.0      0     0 pts/0    Z+   04:28   0:00 [the_walking_dea] <defunct>
    rarylson 22049  0.0  0.0      0     0 pts/0    Z+   04:28   0:00 [the_walking_dea] <defunct>

Neste momento, tínhamos 3 processos zumbis no sistema (estado _defunct_, representado pela letra Z).

É interessante observar que cada processo zumbi possui um PID único (ocupando uma entrada na tabela de processos), possui a informação de dono e terminal (como essas informações são salvas na tabela de processos, o comando `ps` tem acesso a elas), e não consome CPU ou memória.

Após aguardar um tempo, iremos contar a quantidade de processos **the\_walking\_dead** no sistema. Observe que eles estão aumentando indefinidamente:

    :::console
    $ ps aux | grep the_walking | grep -v grep | grep defunct | wc -l
    15

### O processo init e os processos zumbis

O processo **init**, raíz da árvore de processos, possui um [comportamento interessante](http://unix.stackexchange.com/questions/11172/how-can-i-kill-a-defunct-process-whose-parent-is-init#comment14863_11173): de tempos em tempos, este processo verifica se existem processos filhos zumbis e, se existirem, retira-os da tabela de processos do sistema.

Além disso, conforme explicado no artigo [Tipos de processos no Linux]({filename}processos-tipos.md), o comportamento padrão de um processo órfão é ser adotado pelo **init**.

Assim, o que ocorre se eliminarmos um processo pai que possui vários processos zumbis como filhos? Neste caso, o processo **init** irá adotar todos os processos zumbis e, na sequência, irá eliminá-los da tabela de processos.

Podemos verificar este comportamento finalizando o processo pai **the\_walking\_dead** no primeiro terminal (executando `CRTL+C`) e, logo após, vendo que não existem mais processos zumbis no sistema:

    :::console
    Child created and ending... Bye!
    ^C
    $ ps aux | grep the_walking | grep -v grep | grep defunct | wc -l
    0

Usando processos zumbis para esgotar o número máximo de processos
-----------------------------------------------------------------

Em sistemas Linux (e em vários outros _Unix like_), o número máximo de processos que um usuário poderá iniciar pode ser limitado através do mecanismo de segurança **ulimit**. Esta [página do manual do MondoDB](http://docs.mongodb.org/manual/reference/ulimit/) explica muito bem sobre este mecanismo.

Por exemplo, neste artigo estamos executando processos utilizando o usuário de poucos privilégios **rarylson**. Podemos contar quantos processos este usuário está executando através do comando abaixo:

    :::console
    $ ps ax -o user | grep rarylson | wc -l
    7

Iremos, agora, abrir dois terminais: um com um usuário de poucos privilégios, e outro com o usuário **root**. No primeiro terminal, iremos utilizar o comando [`ulimit`](http://www.ss64.com/bash/ulimit.html) para limitar o número de processos que o usuário **rarylson** poderá iniciar:

    :::console
    $ limit -u 17

Você pode executar o comando `ulimit -a` para verificar que a política foi, de fato, aplicada. O valor acima foi escolhido, neste caso particular, como sendo 10 unidades acima do número de processos que este usuário já está executando. 

Agora, iremos novamente executar nosso processo **the\_walking\_dead**:

    :::console
    $ ./the_walking_dead 
    Child created and ending... Bye!
    [...]
    Child created and ending... Bye!
    Error while forking
    Error while forking
    [...]

Vemos que, após algum tempo, o nosso programa não consegue mais criar novos zumbis.

No segundo terminal, iremos contar o número de processos do usuário **rarylson**:

    :::console
    $ ps ax -o user | grep rarylson | wc -l
    16

**Obs:** Se você esteja intrigado com o fato do número de processos do usuário pouco privilegiado ser uma unidade menor que o número máximo configurado, saiba que eu também estou :(! Se souber da resposta, compartilhe!!!

Mesmo com a dúvida remanescente, o exemplo acima nos mostra que o tratamento inadequado de processos zumbis pode impossibilitar que novos processos sejam criados.

Neste exemplo, foi esgotado o número máximo de processos que um usuário pode criar. Entretanto, bastaria deixar nosso usuário sem limites (comando `ulimit -u unlimited`), comentar a linha 11 do nosso programa (que realiza a operação _sleep_), compilá-lo e executá-lo novamente para rapidamente esgotarmos o número de PIDs do sistema.

Por razões óbvias, se for realizar esta experiência, recomendamos o uso de uma máquina virtual :).

O que ainda falta?
------------------

Simulamos a aparição de processos zumbis e mostramos como eles podem esgotar o número de processos de um usuário. Mostramos também um fluxo de execução desejado, que não geraria processos zumbis, e apresentamos o exemplo do Nginx.

Entretanto, não mostramos como implementar um fluxo correto. Deixaremos este assunto para um próximo artigo.

Referências
-----------

- [Wikipedia - Zombie Process](http://en.wikipedia.org/wiki/Zombie_process)
- [Defunct, zombie and immortal processes](http://www-cdf.fnal.gov/offline/UNIX_Concepts/concepts.zombies.txt)
