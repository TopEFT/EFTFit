#include <iostream>
#include <chrono>

using Clock = std::chrono::steady_clock;
using std::chrono::time_point;
using std::chrono::duration_cast;
using std::chrono::milliseconds;

using namespace std;

double findDuration(time_point<Clock> start)
{
    time_point<Clock> end = Clock::now();
    milliseconds diff = duration_cast<milliseconds>(end - start);
    double sec = (double) diff.count();
    return sec/1000.;
}
