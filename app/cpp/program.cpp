#include <iostream>
#include <string>
#include <chrono>

std::string DEFAULT_JOB_ID = "UNKNOWN";
int DEFAULT_DURATION = 10;

double process(std::string job_id, int duration) {
  using namespace std::chrono;

  time_point<system_clock> start = system_clock::now();
  double elapsed_time = 0;
  double prev = 0;

  while (elapsed_time < duration) {
    elapsed_time = duration_cast<seconds>(system_clock::now() - start).count();

    // Print job id and time elapsed every second
    if (elapsed_time != prev) {
      prev = elapsed_time;
      std::cout << "Job id \"" << job_id << "\" elapsed Time: " << elapsed_time << " (s)" << std::endl;
    }
  }

  return elapsed_time;
}

/*
* CPP program that bursts the CPU for some amount of time.
* The first argument to the program is job id (default is "UNKNOWN")
* The second argument to the program is job duration (default is 10s)
*
*/
int main(int argc, char *argv[])
{
  std::string job_id = DEFAULT_JOB_ID;
  int duration = DEFAULT_DURATION;

  if (argc > 2) {
    job_id = std::string(argv[1]);
    duration = std::stoi(argv[2]);
  }

  double elapsed_time = process(job_id, duration);
  std::cout << "Finished process \"" << job_id << "\" in " << elapsed_time << " (s)" << std::endl;
  return 0;
}
