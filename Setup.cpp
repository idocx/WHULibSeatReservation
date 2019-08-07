#include<iostream>
#include<string>
using namespace std;
int main()
{
    
    
    //****若为Linux用户，将cmd改为bash*****
    string commandline="cmd";
    //************************************
    
    
    
    if(commandline=="cmd")
    {
        system("pip install pyqt5 requests");
        system("pause");
    }
    else if(commandline=="bash")
    {
        system("pip3 install pyqt5 requests");
        system("read -n 1 -p \"Press enter to continue...\"");
    }
    return 0;
}
