Title: Processos zumbis: Tratando corretamente (parte 2)
Date: 2014-01-26 18:10
Tags: linux, shell, c, exemplo real
Slug: processos-zumbis-2
Category: Linux
Author: Rarylson Freitas
Summary: Saiba como evitar que seu software gere processos zumbis. Neste artigo, iremos desenvolver corretamente programas em C que não geram processos zumbis. Iremos também analisar como alguns softwares do mundo real tratam este tipo de processo. Por fim, iremos apresentar um exemplo real de software onde uma falha permitia criar infindandamente processos zumbis no sistema.
Status: draft

No primeiro artigo [Processos zumbis: Introdução (parte 1)]({filename}processos-zumbis.md), mostramos o que são processos zumbis e quais são os problemas que podem causar.

Neste artigo, iremos mostrar como evitá-los: mostraremos como desenvolver uma aplicação que execute continuamente sem gerar um alto número de processos zumbis.

Iremos também apresentar situações em que processos zumbis não precisam ser tratados ou em que basta tratá-los de tempo em tempo.

Por fim, iremos mostrar um exemplo real onde o software **Symantec Backup Exec**, em uma versão mais antiga, não tratava corretamente o fim de seus processos filhos, gerando vários processos zumbis no sistema. Iremos mostrar também o _workarround_ utilizado para contornar a situação.

Recaptulando
------------

Dentre os conceitos mais importantes do [artigo passado]({filename}processos-zumbis.md), podemos citar:

- [Processo zumbis](http://en.wikipedia.org/wiki/Zombie_process), também chamados de _zombies_ ou _defuncts_, são processos que terminaram a execução, tiveram seus recursos desalocados, mas ainda possuem uma entrada na tabela de processos;
- Em grande número, podem esgotar o número de PIDs do sistema;
- Os processos, ao finalizarem sua execução, permanecem na tabela de processos para que seu processo pai possa ser notificado do fim de sua execução, analisar o código que o filho retornou, e executar ações necessárias para manter o correto funcionamento da aplicação;
  - Assim, _deamons_ deveriam tratar corretamente seus processos filhos, retirando adequadamente suas entradas da tabela de processos a medida que estes vão finalizando sua execução.

Porque manter uma entrada na tabela de processos?
-------------------------------------------------

Poderia salvar em um arquivo ou em algum outro lugar que não ocupasse entrada na tabela de processos do sistema? **Não**, pois não haveria como identificar unicamente aquele processo. Ao liberar a entrada, o PID torna-se disponível para uso por outro processo, e deixaria de haver uma forma de identificar unicamente o processo que encerrou a execução.

Ver: http://stackoverflow.com/questions/8665642/why-do-i-have-to-wait-for-child-processes

Tratando corretamente
---------------------

Ver: http://stackoverflow.com/questions/8665642/why-do-i-have-to-wait-for-child-processes
modelo 1: wait (e explicar o equivalente usando waitpid)
modelo 2: waitpid( -1, &status, WNOHANG ) dentro de um loop (lança um processo, pergunta se algum filho morreu, lança outro, pergunta novamente)
modelo 3: waitpid( -1, &status, WNOHANG ) usando sinais (apenas lança processos. tratar filhos mortos é feito por sinais)

Exemplo para o programa filho: Ele retorna falha com probabilidade de 25%. Testar usando: `echo $?`

maybe_it_works.c, oxente.c, work_hard_play_hard.c, improved_work_hard_play_hard.c

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
- [Wait system calls - Linux man page](http://linux.die.net/man/2/wait)
- [Linux Processes – Process IDs, fork, execv, wait, waitpid C Functions](http://www.thegeekstuff.com/2012/03/c-process-control-functions/)
