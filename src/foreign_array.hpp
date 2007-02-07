#ifndef _HEADER_SEEN_FOREIGN_ARRAY
#define _HEADER_SEEN_FOREIGN_ARRAY




#include <vector>
#include <stdexcept>




class tSizeChangeNotifier;




class tSizeChangeNotificationReceiver
{
  public:
    virtual ~tSizeChangeNotificationReceiver()
    { }
    virtual void notifySizeChange(tSizeChangeNotifier *master, unsigned size) = 0;
};




class tSizeChangeNotifier
{
    typedef std::vector<tSizeChangeNotificationReceiver *> tNotificationReceiverList;
    tNotificationReceiverList NotificationReceivers;

  public:
    virtual ~tSizeChangeNotifier()
    { }
    virtual unsigned size() const = 0;
    virtual void setSize(unsigned size)
    {
      tNotificationReceiverList::iterator first = NotificationReceivers.begin(),
      last = NotificationReceivers.end();
      while (first != last)
	(*first++)->notifySizeChange(this, size);
    }

    void registerForNotification(tSizeChangeNotificationReceiver *rec)
    {
      NotificationReceivers.push_back(rec);
    }

    void unregisterForNotification(tSizeChangeNotificationReceiver *rec)
    {
      tNotificationReceiverList::iterator first = NotificationReceivers.begin(),
      last = NotificationReceivers.end();
      while (first != last)
      {
	if (rec == *first)
	{
	  NotificationReceivers.erase(first);
	  return;
	}
	first++;
      }
    }
};




template<class ElementT> 
class tForeignArray : public tSizeChangeNotifier, public tSizeChangeNotificationReceiver,
  public boost::noncopyable
{
    ElementT	*&Contents;
    int		&NumberOf;
    unsigned	Unit;
    tSizeChangeNotifier *SlaveTo;
    std::string      Name;

  public:
    tForeignArray(const std::string &name, 
        ElementT *&cts, int &number_of, unsigned unit = 1, tSizeChangeNotifier *slave_to = NULL)
      : Contents(cts), NumberOf(number_of), Unit(unit), SlaveTo(slave_to), Name(name)
    {
      Contents = NULL;
      if (SlaveTo)
      {
	SlaveTo->registerForNotification(this);
	setSizeInternal(SlaveTo->size());
      }
      else
	setSize(0);
    }

    ~tForeignArray()
    {
      if (SlaveTo)
	SlaveTo->unregisterForNotification(this);

      if (!SlaveTo)
	NumberOf = 0;
    }

    unsigned size() const
    {
      return NumberOf;
    }

    unsigned unit() const
    {
      return Unit;
    }

    void deallocate()
    {
      if (Contents != NULL)
	free(Contents);
      Contents = NULL;
    }

    void setSize(unsigned size)
    {
      if (SlaveTo)
	throw std::runtime_error("sizes of slave arrays cannot be changed");
      else
	setSizeInternal(size);
    }
    
    void setup()
    {
      if (!SlaveTo)
	throw std::runtime_error("cannot setup non-slave array");
      else
	setSizeInternal(NumberOf);

    }

    void notifySizeChange(tSizeChangeNotifier *master, unsigned size)
    {
      setSizeInternal(size);
    }

    void setSizeInternal(unsigned size)
    {
      if (!SlaveTo)
	NumberOf = size;
      
      if (Contents != NULL)
	free(Contents);

      if (size == 0 || Unit == 0)
	Contents = NULL;
      else
      {
	Contents = new ElementT[Unit*size];
	if (Contents == NULL)
	  throw std::bad_alloc();
      }

      tSizeChangeNotifier::setSize(size);
    }

    void setUnit(unsigned unit)
    {
      if (unit != Unit)
      {
        Unit = unit;
        setSizeInternal(NumberOf);
      }
    }

    void set(unsigned index, ElementT value)
    {
      if (index >= NumberOf * Unit)
	throw std::runtime_error("index out of bounds");
      if (Contents == NULL)
	throw std::runtime_error("Array unallocated");
      Contents[ index ] = value;
    }

    void setSub(unsigned index, unsigned sub_index, ElementT value)
    {
      set(index * Unit + sub_index, value);
    }

    ElementT get(unsigned index)
    {
      if (index >= NumberOf * Unit)
	throw std::runtime_error("index out of bounds");
      if (Contents == NULL)
	throw std::runtime_error("Array unallocated");
      return Contents[ index ];
    }

    ElementT getSub(unsigned index, unsigned sub_index)
    {
      return get(index * Unit + sub_index);
    }

    tForeignArray &operator=(tForeignArray const &src)
    {
      if (SlaveTo)
        assert(src.size() == SlaveTo->size());
      else
        setSize(src.size());

      setUnit(src.Unit);

      if (src.Contents)
        memcpy(Contents, src.Contents, sizeof(ElementT) * Unit * src.size());
      else
      {
        free(Contents);
        Contents = NULL;
      }

      return *this;
    }
};




#endif
