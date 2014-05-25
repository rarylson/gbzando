Title: Processos zumbis: Exemplo real (parte 3)
Date: 2014-05-25 16:20
Tags: linux, shell, c, processos, zumbis, real
Slug: processos-zumbis-3
Category: Linux
Author: Rarylson Freitas
Summary: Neste artigo, iremos apresentar um caso real de um software que, devido a uma falha, criava vários processos zumbis no sistema. Mais especificamente, este artigo conta uma experiência real vivida com o software Symantec Backup Exec 2010 em um servidor de produção. Iremos mostrar a identificação, o diagnóstico e a solução do problema enfrentado. 

No artigo [Processos zumbis: Introdução (parte 1)]({filename}processos-zumbis.md), mostramos o que são processos zumbis e quais são os problemas que eles podem causar.

Em [Processos zumbis: Tratando corretamente (parte 2)]({filename}processos-zumbis-2.md), mostramos como evitá-los: desenvolvemos uma aplicação que tratava corretamente seus processos filhos, não gerando um grande número de processos zumbis.

Neste artigo, iremos mostrar um exemplo real no qual o software **Symantec Backup Exec**, em uma versão mais antiga (**2010**), não tratava corretamente o fim de seus processos filhos, gerando vários processos zumbis no sistema. Iremos mostrar o diagnóstico do problema, bem como o _workarround_ utilizado para contornar a situação.

Recapitulando
-------------

Dentre os conceitos mais importantes dos artigos anteriores, podemos lembrar:

- Processo zumbis, também chamados de _zombies_ ou _defuncts_, são processos que terminaram a execução, tiveram seus recursos desalocados, mas ainda possuem uma entrada na tabela de processos;
- Em grande número, podem esgotar o número de PIDs do sistema ou o número máximo de processos que um usuário pode executar;
- Eles permanecem na tabela de processos até que seu processo pai realize uma operação _wait_ (por exemplo, utilizando as funções `wait` ou `waitpid`);
- _Deamons_ que executam infindamente no sistema deveriam tratar corretamente seus processos zumbis, analisando o código que o filho retornou, e executando as ações necessárias para manter o correto funcionamento da aplicação.

Backup Exec e o aparecimento de processos zumbis
------------------------------------------------

Certa vez, eu e outros membros da [Vialink](http://www.vialink.com.br) deparamos uma situação interessante onde um _deamon_ gerava um número crescente de processos zumbis. 

Por se tratar de uma situação real com um software conhecido, e por esta situação apresentar muito bem os conceitos apresentados nesta série de artigos, resolvemos compartilhar esta experiência. 

### Descrevendo o problema

Um servidor de um cliente nosso possuia instalado o software **Oracle Database**, um conhecido banco de dados. Dentre as ferramentas utilizadas para realizar o backup deste banco de dados, era utilizado o software **Symantec Backup Exec 2010**.

O Backup Exec, por sua vez, utilizava uma arquitetura servidor/agente. Assim, cada servidor que precisava ter um backup realizado possuia instalado um agente de backup. Como o servidor Oracle utilizava um sistema operacional Linux, era utilizado o agente **Symantec Backup Exec RALUS (Remote Agent for Linux & Unix Servers)**. Mais especificamente, era utilizado o RALUS 4.

Após algum tempo com a solução em produção, percebemos que o backup às vezes falhava.

### Analisando o problema

Verificamos então que existia um número muito grande de processos no sistema. 

    :::bash
    ps aux | grep oracle | grep -v grep | wc -l
    > 18451

Vimos que os processos em excesso eram processos zumbis:

    :::bash
    ps aux | grep oracle | grep -v defunc | grep -v grep | wc -l 
    > 357
    ps aux | grep oracle | grep defunc | grep -v grep | wc -l
    > 18094

Verificamos que estes processos possuiam um processo pai em comum:

    :::bash
    ps -xal | grep defunct | grep -v grep
    > F   UID   PID  PPID PRI  NI    VSZ   RSS WCHAN  STAT TTY        TIME COMMAND
    > [...]
    > 4   500 32719  8102  17   0      0     0 exit   Zs   ?          0:00 [ora] <defunct>
    > 4   500 32720  8102  17   0      0     0 exit   Zs   ?          0:00 [ora] <defunct>
    > 4   500 32721  8102  17   0      0     0 exit   Zs   ?          0:00 [ora] <defunct>
    > [...]

Vimos que todos os processos executavam com o mesmo UID e com o mesmo valor de PPID (PID do processo pai).

O UID 500, no nosso caso, pertencia ao usuário _oracle_. Ou seja, existiam muitos processos executando utilizando o mesmo usuário.

Executamos alguns comandos e descobrimos o problema: o usuário _oracle_ havia atingido seu número limite de processos:

    :::bash
    # total running process running with 'oracle' user
    ps ax -o oracle | wc -l
    > 16383
    # temporary using 'oracle' user
    su oracle
    # running process limit for 'oracle'
    ulimit -a | grep "max user processes"
    > max user processes              (-u) 16384
    # exiting from 'oracle' user's shell
    exit

**Obs:** O primeiro artigo sobre processos zumbis apresenta uma [interessante experiência](/processos-zumbis/#usando-processos-zumbis-para-esgotar-o-numero-maximo-de-processos) onde este mesmo problema é simulado.

Por fim, verificamos quem era o processo de PID 8102:

    :::bash
    ps ax | grep 8102 | grep -v grep
    > 8102 ?        Sl   973:06 /opt/VRTSralus/bin/beremote

Ou seja, o _deamon_ do RALUS não estava tratando adequadamente seus processos zumbis e era responsável pelo acúmulo de processos zumbis no sistema.

### Solucionando o problema

Ao perceber que o software utilizado na solução de backup estava deixando vários processos zumbis no sistema, precisávamos de uma solução que limpasse estes processos da tabela de processos do sistema.

Como não possuíamos acesso ao código-fonte do programa, resolvemos adotar uma solução simples a nível de sistema operacional. Assim, nos baseamos no seguinhe fato (já apresentado no artigo [Tipos de processo no Linux]({filename}processos-tipos.md)): Ao finalizarmos um processo pai, todos os seus processos filhos serão herdados pelo processo **init** e este último, após algum tempo, executará uma rotina de tratamento de processos zumbis.

Assim, adicionamos uma entrada no _crontab_ do sistema (comando `crontab -u root -e`) para reiniciar o _deamon_ em períodos adequados:

    :::bash
    # Restart RALUS every saturday due to a bug that generates zumbie process
    0 14 * * 6 /etc/init.d/VRTSralus.init restart

Com isso, uma vez por semana, forçavamos o processamento dos processos zumbis, liberando PIDs para reuso e permitindo ao usuário _oracle_ executar nossos processos.

Após esta mudança, tivemos nossas rotinas de backup novamente operacionais, rodando sem apresentar problemas.

Referências
-----------

- [Wikipedia - Zombie Process](http://en.wikipedia.org/wiki/Zombie_process)
- [Signals (and Zombie and SIGCHLD)](http://www.win.tue.nl/~aeb/linux/lk/lk-5.html)
