#include<iostream>
#include<string>
using namespace std;
int main()
{
    
    
    //****若为Linux用户，将cmd改为bash*****
    string commandline="cmd";
    //************************************
    
    if(commandline=="cmd")
        system("python main_win.py");
    else if(commandline=="bash")
        system("python3 main_win.py");
    return 0;
}
