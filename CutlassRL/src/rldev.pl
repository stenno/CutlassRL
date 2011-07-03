#!/usr/bin/perl
$args = join " ", @ARGV;
if (system("python ./main.py $args 2> ./debug") == 0){
    exit();
}else{
    print `reset`;
    print "Debug output:\n";
    print `cat ./debug`;
    print `rm ./debug`;
    <STDIN>
}