using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GroundStation
{
    class CSVRead
    {
        public List<List<string>> CSV = new List<List<string>>();


        public CSVRead(string csvFile)
        {
            StreamReader reader = new StreamReader(File.OpenRead(csvFile));
            List<string> listA = new List<string>();
            List<string> listB = new List<string>();
            while (!reader.EndOfStream)
            {
                string line = reader.ReadLine();
                string[] values = line.Split(',');

                int idx = 0;
                foreach (string value in values)
                {
                    if (CSV.Count() < idx + 1)
                    {
                        CSV.Add(new List<string>());
                    }
                    CSV[idx].Add(value);
                    idx++;
                }
            }
        }
    }
}
